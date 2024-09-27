import unittest
import os
import sys

import requests

current = os.path.dirname(os.path.realpath(__file__))
subparent = os.path.dirname(current)
parent = os.path.dirname(subparent)
root =   os.path.dirname(parent)
sys.path.append(subparent)
sys.path.append(parent)
sys.path.append(root)
import env
import pandas as pd 
import gspread
from google.oauth2.service_account import Credentials


auth_gc = os.environ.get(f'auth_gc')
gc = gspread.service_account(filename=auth_gc)

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1CTWgP_59_HHDEOOEyJuEHyQCcrBWw95QraUptvePtk0"
SAMPLE_RANGE_NAME = "Class Data!A2:E"
sheet_id = SAMPLE_SPREADSHEET_ID

def get_sheet_by_title(title,skip):
    sht1 = gc.open_by_key(sheet_id)
    wh=sht1.worksheet(title)
    data = wh.get_all_values()   
    if skip==True:
        headers = data.pop(0) 
        headers = data.pop(0) 
    headers = data.pop(0) 
    df = pd.DataFrame(data, columns=headers)
    return df

def get_sheet_share_by_sheet_id(sheet_id,title,skip):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.readonly']
    # Load credentials from the service account file
    creds = Credentials.from_service_account_file(auth_gc, scopes=scope)
    # Authorize the client
    client = gspread.authorize(creds)
    # Open the Google Sheet by its ID
    sht1 = client.open_by_key(sheet_id)
    wh=sht1.worksheet(title)
    data = wh.get_all_values()   
    if skip==True:
        headers = data.pop(0) 
        headers = data.pop(0) 
    headers = data.pop(0) 
    df = pd.DataFrame(data, columns=headers)
    return df

def checkExistSheet(client, sheet_name, spreadsheet_id=None):
    if spreadsheet_id is None:
        spreadsheet_id = sheet_id
    spreadsheet = client.open_by_key(spreadsheet_id)
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        print(f"exist sheet with name : {sheet_name}")
        return False
    return True

def open_worksheet(sheet_name, spreadsheet_id=None):
    """
    Write a pandas DataFrame to a new sheet in the specified Google Spreadsheet.
    If no spreadsheet_id is provided, it uses the default sheet_id from the environment.
    """
    if spreadsheet_id is None:
        spreadsheet_id = sheet_id

    # Authorize and open the spreadsheet
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(auth_gc, scopes=scope)
    client = gspread.authorize(creds)
    # spreadsheet_id tu browser can chia se cho email
    # trong json file env : "client_email": "glassdoorjob@glassdoorjoblisting.iam.gserviceaccount.com"
    # thi moi co quyen edit sheet
    spreadsheet = client.open_by_key(spreadsheet_id)

    # Create a new worksheet or clear an existing one
    if not checkExistSheet(client, sheet_name, spreadsheet_id):
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1, cols=1)
    else:
        worksheet = spreadsheet.worksheet(sheet_name)
        worksheet.clear()
    return worksheet

def write_data_to_sheet(df, worksheet):

    # Convert DataFrame to list of lists
    data = [df.columns.tolist()] + df.values.tolist()

    # Update the worksheet
    try:
        worksheet.update(data)
    except requests.exceptions.JSONDecodeError:
        print(f"DataFrame values ==> '{df.values.tolist()}'")
    # print(f"DataFrame successfully written to sheet '{sheet_name}'")

def write_dataframe_to_sheet(df, sheet_name, spreadsheet_id=None):
    """
    Write a pandas DataFrame to a new sheet in the specified Google Spreadsheet.
    If no spreadsheet_id is provided, it uses the default sheet_id from the environment.
    """
    if spreadsheet_id is None:
        spreadsheet_id = sheet_id

    # Authorize and open the spreadsheet
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(auth_gc, scopes=scope)
    client = gspread.authorize(creds)
    # spreadsheet_id tu browser can chia se cho email
    # trong json file env : "client_email": "glassdoorjob@glassdoorjoblisting.iam.gserviceaccount.com"
    # thi moi co quyen edit sheet
    spreadsheet = client.open_by_key(spreadsheet_id)

    # Create a new worksheet or clear an existing one
    if not checkExistSheet(client, sheet_name, spreadsheet_id):
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1, cols=1)
    else:
        worksheet = spreadsheet.worksheet(sheet_name)
        worksheet.clear()

    # Convert DataFrame to list of lists
    data = [df.columns.tolist()] + df.values.tolist()

    # Update the worksheet
    try:
        worksheet.update(data)
    except gspread.exceptions.APIError:
        print(f"DataFrame values ==> '{df.values.tolist()}'")
    print(f"DataFrame successfully written to sheet '{sheet_name}'")
if __name__ == "__main__":
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.readonly']
    # Load credentials from the service account file

    # creds = Credentials.from_service_account_file('/Users/nghiahuynh/Documents/UiPath/jobhunting-main/jobhunting-436610-e1998661ea82.json', scopes=scope)
    # Authorize the client
    # client = gspread.authorize(creds)
    # Open the Google Sheet by its ID
    # sht1 = client.open_by_key('1bSp1l79Jr7b9k3nBXWsNKEgAx-DpkFhGNRblX0q5zAo').sheet1
    # print (sht1)
    # print (gc.open_by_url("https://docs.google.com/spreadsheets/d//edit?usp=sharing"))
    # print (get_sheet_by_title("Basic Information",True))

    # Set up the scope
   
    # print (sheet)
    # print (client.list_spreadsheet_files(folder_id='0ADIvex3xDa6eUk9PVA'))
    # sheet = client.open_by_key(sheet_id, driveId='0ADIvex3xDa6eUk9PVA').sheet1

    # Read data from the sheet
    test_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    write_dataframe_to_sheet(test_df, 'Hello','1T0TvP8urGMhnlXdZ84RjHTXTTRf-WzZc9IRDBl1T0SQ')
    # Print the data
    # for row in data:
    #     print(row)