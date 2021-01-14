# Standard Library
from functools import cached_property

# Third Party Library
from django.conf import settings
from gspread import (
    Spreadsheet,
    Worksheet,
)
from gspread_formatting import get_user_entered_format

# Application Library
from constants import PaperFormat
from finder.google_table_logic.client import get_gspread_client
from helpers import cached_method

TEMPLATES_CACHE_KEY = "CELL_TEMPLATES"
ANSWER_LIST_CACHE_KEY = "ANSWER_LIST"


def get_template_cache_key(*args, **kwargs):
    return TEMPLATES_CACHE_KEY


def get_answer_list_cache_key(*args, **kwargs):
    return ANSWER_LIST_CACHE_KEY


# TODO: add typings to properties
class GoogleTableDataManager:
    def __init__(self, order: int):
        self.order = order
        self._client = get_gspread_client()

    @cached_property
    def _document(self) -> Spreadsheet:
        return self._client.open("Transfercopy")

    @cached_property
    def _search_sheet(self) -> Worksheet:
        return self._document.worksheet("Производство")

    @cached_property
    def _answer_sheet(self) -> Worksheet:
        return self._document.worksheet("telegram-bot")

    @cached_property
    def cell_templates(self):
        return self._get_cell_templates()

    @cached_property
    def answers_list(self):
        return self._get_answers_list()

    @cached_method(get_template_cache_key, settings.TEMPLATES_CACHE_TTL)
    def _get_cell_templates(self):
        templates = {}
        for paper_format in PaperFormat:
            templates[paper_format] = get_user_entered_format(
                self._search_sheet, paper_format.value
            ).backgroundColor
        return templates

    @cached_method(get_answer_list_cache_key, settings.ANSWERS_LIST_TTL)
    def _get_answers_list(self):
        return self._answer_sheet.col_values(4)
