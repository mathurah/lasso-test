from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import date

SCOPES = ['https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive.metadata'
          ]
COLUMN_TITLES = ['Name', 'Current Role', 'Current Firm', 'Profile Picture']
SOURCING_FOLDER_ID = '12PGD5KukCIgrRRYoEJw260PUopitcILx'
NEW_LEADS_SHEET = 'New Leads'
ALL_LEADS_SHEET = 'All Leads'
FILE_NAME = 'Sydney'

SETUP_SHEETS_REQUEST = {
    "requests": [
        {
            "addSheet": {
                "properties": {
                    "title": NEW_LEADS_SHEET,
                }
            },
        },
        {
            "addSheet": {
                "properties": {
                    "title": ALL_LEADS_SHEET,
                }
            },
        },
        {
            "deleteSheet": {
                "sheetId": 0
            }
        },
    ]
}


class Drive:

    def __init__(self):
        creds = None
        if os.path.exists('credentials/drive_token.pickle'):
            with open('credentials/drive_token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/drive_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('credentials/drive_token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)

    def move_file(self, file_id):
        # Retrieve the existing parents to remove
        file = self.service.files().get(fileId=file_id,
                                        fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        # Move the file to the new folder
        file = self.service.files().update(fileId=file_id,
                                           addParents=SOURCING_FOLDER_ID,
                                           removeParents=previous_parents,
                                           fields='id, parents').execute()


class Sheets:

    def __init__(self):
        creds = None
        if os.path.exists('credentials/sheets_token.pickle'):
            with open('credentials/sheets_token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/sheets_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('credentials/sheets_token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    @staticmethod
    def convert_leads_to_rows(leads):
        rows = [COLUMN_TITLES]
        for lead in leads:
            rows.append([lead['name'], lead['current_position'], lead['current_company'], lead['image_url']])
        print(len(leads))
        return rows

    def create_spreadsheet(self, new, all):
        date_string = str(date.today())
        spreadsheet = {
            'properties': {
                'title': FILE_NAME + ' ' + date_string
            }
        }

        print('Create Spreadsheet')
        spreadsheet = self.service.spreadsheets().create(body=spreadsheet,
                                                         fields='spreadsheetId').execute()
        spread_sheet_id = spreadsheet.get('spreadsheetId')

        print('Update Tabs')
        response = self.service.spreadsheets().batchUpdate(
            spreadsheetId=spread_sheet_id, body=SETUP_SHEETS_REQUEST).execute()

        new_leads_id = response['replies'][0]['addSheet']['properties']['sheetId']
        all_leads_id = response['replies'][1]['addSheet']['properties']['sheetId']

        new_leads = self.convert_leads_to_rows(new)
        all_leads = self.convert_leads_to_rows(all)
        data = [{
            'range': NEW_LEADS_SHEET,
            'values': new_leads
        }, {
            'range': ALL_LEADS_SHEET,
            'values': all_leads
        }]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }

        print('Upload Leads to Sheets')
        result = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spread_sheet_id, body=body).execute()
        print('{0} cells updated.'.format(result.get('updatedCells')))
        return spread_sheet_id, [new_leads_id, all_leads_id]

    def resize_columns(self, sheet_id, sheet_ids):
        update_widths = {
            "requests": [
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_ids[0],
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": len(COLUMN_TITLES)
                        }
                    }
                },
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_ids[1],
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": len(COLUMN_TITLES)
                        }
                    }
                },
            ]
        }
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id, body=update_widths).execute()
