# Standard Library
import json
from dataclasses import (
    InitVar,
    asdict,
    dataclass,
    field,
)
from typing import (
    Dict,
    List,
    Optional,
)

# Third Party Library
from authlib.integrations.requests_client import AssertionSession
from django.conf import settings
from google.auth.transport.requests import AuthorizedSession
from gspread import Client
from gspread.utils import convert_credentials

# Application Library
from finder.google_table_logic.constants import SCOPES

gspread_client = None


class GSpreadClient(Client):
    def __init__(self, auth=None, session=None):
        self.auth = auth and convert_credentials(auth)
        self.session = session or AuthorizedSession(self.auth)


@dataclass
class Creds:
    conf: InitVar[dict]
    scopes: InitVar[List[str]] = None
    subject: Optional[str] = None
    header: Dict[str, str] = field(default_factory=lambda: {"alg": "RS256"})
    grant_type: str = AssertionSession.JWT_BEARER_GRANT_TYPE

    token_endpoint: str = field(init=False)
    issuer: str = field(init=False)
    audience: str = field(init=False)
    claims: Dict[str, str] = field(init=False)
    key: str = field(init=False)

    def __post_init__(self, conf: dict, scopes: List[str]):
        self.token_endpoint = conf["token_uri"]
        self.issuer = conf["client_email"]
        self.audience = self.token_endpoint
        self.claims = {"scope": " ".join(scopes or SCOPES)}
        self.key = conf["private_key"]
        key_id = conf.get("private_key_id")
        if key_id:
            self.header["kid"] = key_id


def create_assertion_session(conf_file, scopes=None, subject=None):
    with open(conf_file, "r") as f:
        return AssertionSession(**asdict(Creds(json.load(f), scopes, subject)))


def get_gspread_client() -> GSpreadClient:
    global gspread_client
    return gspread_client or set_gspread_client()


def set_gspread_client():
    global gspread_client
    gspread_client = GSpreadClient(
        session=create_assertion_session(settings.KEY_FILE_PATH)
    )
    return gspread_client
