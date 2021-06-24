from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

GOOGLE_SCOPES = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('service-key.json', GOOGLE_SCOPES)

gauth = GoogleAuth()
gauth.credentials = creds

drive = GoogleDrive(gauth)

# Now do stuff as normal!
