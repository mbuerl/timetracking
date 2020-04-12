from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class cCalendarOperations:
    def __init__(self):
        self.creds = None

    def token_operator(self):
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials_matthias.json', SCOPES
                    )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.creds, token)
        return self.creds

    def get_calendars(self):
        login_identity = self.token_operator()

        service = build('calendar', 'v3', credentials=login_identity)
        page_token = None
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            print (calendar_list)
            for calendar_list_entry in calendar_list['items']:
                # print (calendar_list_entry)
                print ("hi")
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break


    def get_events(self):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        login_identity = self.token_operator()

        service = build('calendar', 'v3', credentials=login_identity)
        service1 = build('calendar', 'v3', credentials=login_identity)

        calendar_list_entry = service1.calendarList().get(calendarId='calendarId').execute()
        print (type(calendar_list_entry))
        
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now, 
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
            ).execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])


if __name__ == '__main__':
    calops = cCalendarOperations()
    calops.get_calendars()