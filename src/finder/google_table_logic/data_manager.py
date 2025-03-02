# Standard Library
import logging
import re
from contextlib import suppress
from dataclasses import (
    InitVar,
    dataclass,
    field,
)
from functools import (
    cached_property,
    partial,
)
from time import sleep
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

# Third Party Library
from django.conf import settings
from gspread import (
    Spreadsheet,
    Worksheet,
)
from gspread_formatting import (
    CellFormat,
    get_user_entered_format,
)

# Application Library
from constants import PaperFormat
from finder.google_table_logic.client import get_gspread_client
from helpers import cached_method

logger = logging.getLogger(settings.PROJECT)

CellTemplate = Dict[PaperFormat, Optional[str]]

TEMPLATES_CACHE_KEY = "CELL_TEMPLATES"
ANSWER_LIST_CACHE_KEY = "ANSWER_LIST"
ORDERS_CACHE_KEY = "ORDER_{order_id}"


def get_template_cache_key(*args, **kwargs):
    return TEMPLATES_CACHE_KEY


def get_answer_list_cache_key(*args, **kwargs):
    return ANSWER_LIST_CACHE_KEY


def get_orders_cache_key(_, order_id: int):
    return ORDERS_CACHE_KEY.format(order_id=order_id)


@dataclass
class TableData:
    order: InitVar[str]
    search_sheet: InitVar[Worksheet]

    cell_coordinates: Tuple[int, int] = field(init=False)
    cell_address: str = field(init=False)
    steel_type: str = field(init=False)
    steel_depth: str = field(init=False)
    user_cell_color: Optional[str] = field(init=False)
    user_f_row_color: Optional[str] = field(init=False)

    def __post_init__(self, order: str, search_sheet: Worksheet):
        row = int(re.search(r"(R[0-9]+)", order).group(0)[1:])  # type: ignore
        column = int(
            re.search(r"(C[0-9]+)", order).group(0)[1:]  # type: ignore
        ) - 1
        self.cell_coordinates = (row, column)
        self.cell_address = search_sheet.cell(row, column).address
        self.steel_type = search_sheet.cell(row, 4).value
        self.steel_depth = search_sheet.cell(row, 5).value

        self.user_cell_color = get_format_safe(
            get_user_entered_format, search_sheet, self.cell_address
        ).backgroundColor
        self.user_f_row_color = get_format_safe(
            get_user_entered_format, search_sheet, f"F{row}"
        ).backgroundColor


class GoogleTableDataManager:
    RESULT_TEMPLATE = "Детали из {steel_type} " \
                      "толщиной {steel_depth} мм - {answer}"
    CASES: List[Tuple[Callable[[TableData, CellTemplate], bool], int]] = [
        (lambda data, ts: data.user_cell_color == ts[PaperFormat.A5], 8),
        (
            lambda data, ts: data.user_cell_color == ts[
                PaperFormat.A3
            ] and data.user_f_row_color == ts[PaperFormat.A4],
            6
        ),
        (lambda data, ts: data.user_cell_color == ts[PaperFormat.A4], 7),
        (
            lambda data, ts: data.user_cell_color == ts[
                PaperFormat.A3
            ] and data.user_f_row_color == ts[PaperFormat.A3],
            5
        ),
    ]
    DEFAULT_ANSWER_NUMBER = 4

    def __init__(self):
        self._client = get_gspread_client()

    @cached_property
    def _document(self) -> Spreadsheet:
        logger.debug(f"Get worksheet '{settings.DOCUMENT_NAME}'")
        return self._client.open(settings.DOCUMENT_NAME)

    @cached_property
    def search_sheet(self) -> Worksheet:
        logger.debug(f"Get worksheet '{settings.SEARCH_SHEET_NAME}'")
        return self._document.worksheet(settings.SEARCH_SHEET_NAME)

    @cached_property
    def answer_sheet(self) -> Worksheet:
        logger.debug(f"Get worksheet '{settings.ANSWER_SHEET_NAME}'")
        return self._document.worksheet(settings.ANSWER_SHEET_NAME)

    @cached_property
    def cell_templates(self):
        logger.debug("Get cell templates")
        return self._get_cell_templates()

    @cached_property
    def answers_list(self):
        logger.debug("Get answers list")
        return self._get_answers_list()

    @cached_method(get_template_cache_key, settings.TEMPLATES_CACHE_TTL)
    def _get_cell_templates(self) -> CellTemplate:
        templates = {}
        for paper_format in PaperFormat:
            templates[paper_format] = get_format_safe(
                get_user_entered_format,
                self.answer_sheet,
                paper_format.value
            ).backgroundColor
        logger.debug("Get cell templates")
        return templates

    @cached_method(get_answer_list_cache_key, settings.ANSWERS_LIST_TTL)
    def _get_answers_list(self) -> list:
        logger.debug("Get answers list from server")
        return self.answer_sheet.col_values(4)

    def get_answer_number(self, table_data: TableData) -> int:
        for case, answer_number in self.CASES:
            if case(table_data, self.cell_templates):
                return answer_number
        return self.DEFAULT_ANSWER_NUMBER

    @cached_method(get_orders_cache_key, settings.ORDERS_TTL)
    def process_order(self, order_id: int) -> List[str]:
        compiled_order_id = re.compile(str(order_id))
        orders = self.search_sheet.findall(compiled_order_id)
        logger.debug(f"Get {len(orders)} orders")
        results = []
        if orders:
            for order in map(str, orders):
                table_data = TableData(order, self.search_sheet)
                logger.debug(table_data)
                answer_number = self.get_answer_number(table_data)
                result = self.RESULT_TEMPLATE.format(
                    steel_type=table_data.steel_type,
                    steel_depth=table_data.steel_depth,
                    answer=self.answers_list[answer_number],
                )
                results.append(result)
                sleep(settings.ORDER_TIMEOUT)
        else:
            results.append(f"{order_id} - {self.answers_list[3]}")

        return results


@dataclass
class FakeFormat:
    backgroundColor: Optional[str] = None


def get_format_safe(
        format_getter: Callable, *args, **kwargs
) -> Union[CellFormat, FakeFormat]:
    format_getter = partial(format_getter, *args, **kwargs)
    cell_format = None
    with suppress(KeyError, AttributeError, TypeError):
        cell_format = format_getter(*args, **kwargs)

    return cell_format or FakeFormat()
