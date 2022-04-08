import gspread
from session_gsheet import Session

gc = gspread.service_account(filename='filename.json')
sheet = gc.open_by_key("KEY")
worksheet = sheet.sheet1


#session = Session(worksheet)
#print(session.check_for_duplicates([1]))
