import base64
import email
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def auth():
    scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


def get_emails():
    creds = auth()
    service = build("gmail", "v1", credentials=creds)
    result = service.users().messages().list(userId="me").execute()
    messages = result.get("messages")

    for msg in messages:
        txt = service.users().messages().get(userId="me", id=msg["id"]).execute()
        try:
            payload = txt["payload"]
            headers = payload["headers"]
            subject = sender = ""
            for d in headers:
                if d["name"] == "Subject":
                    subject = d["value"]
                if d["name"] == "From":
                    sender = d["value"]
            # The Body of the message is in Encrypted format. So, we have to decode it.
            # Get the data and decode it with base 64 decoder.
            if parts := payload.get("parts"):
                parts = parts[0]
                data = parts["body"]["data"]
                data = data.replace("-", "+").replace("_", "/")
            print("Subject: ", subject)
            print("From: ", sender)
            print("\n")
        except Exception as e:
            print(e)
            pass


get_emails()
