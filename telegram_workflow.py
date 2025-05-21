import os
from telegram.ext import Updater, MessageHandler, Filters
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from datetime import datetime

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/calendar']

def get_google_creds():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def send_email(service, message_text):
    import base64
    from email.mime.text import MIMEText
    
    message = MIMEText(message_text)
    message['to'] = 'YOUR_EMAIL@gmail.com'  # Replace with your email
    message['subject'] = 'New Invoice from Telegram'
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        return True
    except Exception as e:
        print(f'An error occurred: {e}')
        return False

def create_calendar_event(service, message_text):
    # Basic event creation - you might want to parse the message for more details
    event = {
        'summary': 'Event from Telegram',
        'description': message_text,
        'start': {
            'dateTime': datetime.now().isoformat(),
            'timeZone': 'Your/Timezone',  # Replace with your timezone
        },
        'end': {
            'dateTime': datetime.now().isoformat(),
            'timeZone': 'Your/Timezone',  # Replace with your timezone
        },
    }
    
    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return True
    except Exception as e:
        print(f'An error occurred: {e}')
        return False

def handle_message(update, context):
    message_text = update.message.text.lower()
    
    if 'invoice' in message_text:
        # Handle invoice - send email
        creds = get_google_creds()
        gmail_service = build('gmail', 'v1', credentials=creds)
        if send_email(gmail_service, update.message.text):
            update.message.reply_text('Message sent to Gmail!')
        else:
            update.message.reply_text('Failed to send email.')
            
    elif 'calendar' in message_text:
        # Handle calendar - create event
        creds = get_google_creds()
        calendar_service = build('calendar', 'v3', credentials=creds)
        if create_calendar_event(calendar_service, update.message.text):
            update.message.reply_text('Calendar event created!')
        else:
            update.message.reply_text('Failed to create calendar event.')
            
    else:
        update.message.reply_text('Command not recognized.')

def main():
    # Initialize the bot
    updater = Updater('YOUR_BOT_TOKEN', use_context=True)  # Replace with your bot token
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    # Add message handler
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()