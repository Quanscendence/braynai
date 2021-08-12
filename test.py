import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


# scope=['htps://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# creadentials = ServiceAccountCredentials.from_json_keyfile_name('Google-sheets-75d74ec3a465.json')
# gc = gspread.authorize(creadentials)
# wks = gc.open('test integration').sheet1

# data = wks.get_all_records()
# df = pd.DataFrame(data)
# print(df)