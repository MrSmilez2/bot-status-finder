# Standard Library
from typing import List

# Third Party Library
import gspread
from django.conf import settings
from gspread import Client
from oauth2client.service_account import ServiceAccountCredentials

# Application Library
from finder.gspread_logic.constants import SCOPES


class GSpreadClient:
    def __init__(
            self,
            scopes: List[str] = None,
            creds: ServiceAccountCredentials = None
    ):
        self.scopes = scopes or SCOPES
        self.creds = creds or ServiceAccountCredentials.from_json_keyfile_name(
            settings.KEY_FILE_PATH,
            scopes=self.scopes
        )
        self._client: Client = gspread.authorize(self.creds)
