# main.py
# This file serves as the main entry point for the automation script that handles lead management
# for TechNova Solutions using Zapier, Google Sheets, and Gmail.

import os
import time
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

# Configuration for Google Sheets API and Gmail API
SHEET_ID = 'your-google-sheet-id-here'
SHEET_NAME = 'Lead_Data'
GMAIL_API_SCOPE = 'https://www.googleapis.com/auth/gmail.send'

def authenticate_google_services():
    """
    Authenticates Google Sheets API and Gmail API using OAuth credentials.
    """
    try:
        creds, project = google.auth.default(scopes=[GMAIL_API_SCOPE])
        if not creds.valid:
            creds.refresh(Request())

        # Google Sheets API client
        sheets_service = build('sheets', 'v4', credentials=creds)

        # Gmail API client
        gmail_service = build('gmail', 'v1', credentials=creds)

        return sheets_service, gmail_service

    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        exit(1)

def retrieve_leads(sheets_service):
    """
    Retrieves lead data from Google Sheets.
    """
    range_ = f"{SHEET_NAME}!A2:F"  # Specify the correct range
    result = sheets_service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range=range_).execute()
    leads = result.get('values', [])
    return leads

def calculate_lead_score(lead_data):
    """
    Calculate the lead score based on predefined criteria.
    Example criteria: Company Size, Budget, and Urgency.
    """
    score = 0
    # Extract values from the lead_data array (adjust indexes as per your data structure)
    company_size = lead_data[1]  # e.g., Column B for company size
    budget = lead_data[2]  # e.g., Column C for annual budget
    urgency = lead_data[3]  # e.g., Column D for urgency

    # Add score based on conditions (example criteria)
    if company_size == '1000+ employees':
        score += 30
    if budget == 'More than $100,000':
        score += 40
    if urgency == 'Immediate (within 1 month)':
        score += 30

    return score

def send_welcome_email(gmail_service, lead_data):
    """
    Sends a welcome email to leads with a score above a threshold (e.g., 70).
    """
    lead_name = lead_data[0]  # e.g., Column A for lead name
    subject = "Welcome to TechNova Solutions!"
    body = f"Hi {lead_name},\n\nThank you for reaching out to us! We appreciate your interest and will get back to you soon."

    try:
        message = create_message('your-email@example.com', lead_data[4], subject, body)  # Adjust email field accordingly
        send_message(gmail_service, 'me', message)
        print(f"Welcome email sent to {lead_name}")

    except Exception as e:
        print(f"Error sending email to {lead_name}: {str(e)}")

def create_message(sender, to, subject, body):
    """
    Creates a message to send via Gmail.
    """
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(body)
    message.attach(msg)
    raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    return raw_message

def send_message(service, sender, message):
    """
    Sends the created email message using Gmail API.
    """
    try:
        message = service.users().messages().send(userId=sender, body=message).execute()
        print(f'Message sent successfully: {message["id"]}')
    except Exception as error:
        print(f'An error occurred while sending message: {error}')

def main():
    # Step 1: Authenticate Google Sheets and Gmail API services
    sheets_service, gmail_service = authenticate_google_services()

    # Step 2: Retrieve leads from Google Sheets
    leads = retrieve_leads(sheets_service)

    # Step 3: Process each lead
    for lead in leads:
        lead_score = calculate_lead_score(lead)

        # Step 4: Take action based on lead score
        if lead_score > 70:
            send_welcome_email(gmail_service, lead)

        # Additional actions for leads below score threshold (e.g., nurturing, logging in another sheet) can be added here.

    print("Lead management process completed.")

if __name__ == '__main__':
    main()
