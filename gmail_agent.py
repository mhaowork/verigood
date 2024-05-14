import base64
import os.path
import time
from openai import OpenAI
import pyperclip
import platform
import email

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def process_email(subject, body):
    # Use OpenAI to extract validation code from the email body
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
                "role": "system",
                "content": """
                    You are a helpful assistant that helps users extract validation codes / login links / magic links from emails.
                    First, you need to check the email subject and body if this email is for validation purpose to verify account ownership.
                    These emails usually contain a one-time code or login link to authenticate the user. If it's not a verification email, you should return N/A (no quotes).
                    Otherwise, your response should contain only the validation code OR a login link starting with http(s). No quotes needed in the result.
                """,
            },
            {
                "role": "user",
                "content": "Subject: "
                + subject
                + "\nBody: \n```\n"
                + body
                + "\n```\n",
            },
        ],
    )
    print("GPT result: ", completion.choices[0].message)
    validation_code_or_link = completion.choices[0].message.content
    if validation_code_or_link == "N/A":
       print("No validation code or link found in the email")
       return
    # Copy the validation code to the clipboard
    pyperclip.copy(validation_code_or_link)
    if platform.system() == "Darwin": # macOS only: play a beep sound
        os.system('say -v Bells "beep"')

def fetch_email(email_id, creds):
    service = build("gmail", "v1", credentials=creds)
    user_id = "me"
    msg = service.users().messages().get(userId=user_id, id=email_id, format="raw").execute()
    # Parse email
    body = ""
    try:
        mime_msg = email.message_from_bytes(base64.urlsafe_b64decode(msg['raw']))
        from_name = mime_msg['from']
        subject = mime_msg['subject']
        print(f"From: {from_name}\nSubject: {subject}\nBody: {body}\n")
        message_main_type = mime_msg.get_content_maintype()
        if message_main_type == 'multipart':
            for part in mime_msg.get_payload():
                if part.get_content_maintype() == 'text':
                    body += part.get_payload() + "\n"
        elif message_main_type == 'text':
            body = mime_msg.get_payload()
    except Exception as e:
        print(f"An error occurred parsing email: {e}")
    if len(body) > 20000:
        print(f'Email body too long (length: {len(body)}, email_id: {email_id}), skipping')
        return
    process_email(subject, body)

def poll_for_new_emails(creds):
    service = build("gmail", "v1", credentials=creds)
    user_id = "me"
    # Get the current mailbox's profile information
    profile = service.users().getProfile(userId=user_id).execute()
    # Get the historyId from the profile
    start_history_id = profile['historyId']
    while True:
        try:
            history = (
                service.users()
                .history()
                .list(userId=user_id, startHistoryId=start_history_id)
                .execute()
            )
            changes = history["history"] if "history" in history else []
            if 'nextPageToken' in history:
                page_token = history['nextPageToken']
            else:
                page_token = None

            while page_token:
                history = (service.users().history().list(userId=user_id, startHistoryId=start_history_id,
                                                          pageToken=page_token).execute())
                changes.extend(history['history'])
                if 'nextPageToken' in history:
                    page_token = history['nextPageToken']
                else:
                    page_token = None

            start_history_id = history['historyId']
            for change in changes:
                if 'messagesAdded' in change:
                    for message in change['messagesAdded']:
                        msg = message['message']
                        print(f"New email received: {msg}")
                        fetch_email(msg['id'], creds)
            time.sleep(0.8)
        except Exception as error:
            print(f"An error occurred, retrying: {error}")


def main():
  creds = None
  SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
  if os.environ.get("OPENAI_API_KEY") is None:
      print("Please set the OPENAI_API_KEY environment variable")
      return
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    # If modifying these scopes, delete the file token.json.
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=54461, open_browser=False)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  print("Started Gmail agent, monitoring")
  poll_for_new_emails(creds)


if __name__ == "__main__":
  main()
