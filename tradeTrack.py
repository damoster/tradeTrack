#!/usr/bin/env python
# __author__ = "David Mo"
# __email__ = "davidmo3576@gmail.com"
# __status__ = "Production"

# Authentication base code from https://developers.google.com/gmail/api/quickstart/python 

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from apiclient import errors
import email
import base64
import re

import tradeTracker # Separate module file with main tradeTracker module

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

"""Get a list of Messages from the user's mailbox.
   NOTE: list only contains 'id' and 'threadId'
"""
# Function from Google API page
# https://developers.google.com/gmail/api/v1/reference/users/messages/list#try-it
def ListMessagesMatchingQuery(service, user_id, query=''):
  """List all Messages of the user's mailbox matching the query.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

  Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError as error:
    print('An error occurred: %s' % error)

# """Get Message with given ID.
# """
# Function from Google API page
# https://developers.google.com/gmail/api/v1/reference/users/messages/get
def GetMimeMessage(service, user_id, msg_id):
  """Get a Message and use it to create a MIME Message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A MIME Message, consisting of data from Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='raw').execute()
    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII')).decode('utf-8')
    mime_msg = email.message_from_string(msg_str)

    return mime_msg

  except errors.HttpError as error:
    print('An error occurred: %s' % error)

# Given a MimeMessage object, return the 'text' body
def getTextBodyFromMimeMsg(mime_msg):
    messageMainType = mime_msg.get_content_maintype()
    if messageMainType == 'multipart':
            for part in mime_msg.get_payload():
                    if part.get_content_maintype() == 'text':
                            return part.get_payload()
            return ""
    elif messageMainType == 'text':
            return mime_msg.get_payload()

def processMimeMsgforTradeTrack(tradeTrack, mime_msg):
    date = mime_msg['Date']
    subject = mime_msg['Subject']
    txtBody = base64.urlsafe_b64decode(getTextBodyFromMimeMsg(mime_msg)).decode("utf-8")
    # print("{}\n{}\n{}".format(date, subject, txtBody))
    
    # Skip email if it is not a trade confirmation email with the following format subject
    # "CommSec - BUB Equity Trade Confirmation"
    # TODO update this later to handle other securities
    if not re.match(r'^CommSec - [A-Z]{3} Equity Trade Confirmation', subject):
        return
    
    # Get all the relevant information and store in the tradeTrack
    stockCode = re.sub(r'^CommSec - ([A-Z]{3}) Equity Trade Confirmation', r'\1', subject)

    # Just for debugging
    # txtBody = 'Attached is an electronic confirmation confirming that we have SOLD for you 5000 units in CRESO PHARMA LTD FPO today on Account 2677206'
    # txtBody = 'Attached is an electronic confirmation confirming that we have BOUGHT for you 14700 units in ESENSE-LAB LTD CDI 1:1 at 0.340 on Account 2677206.'

    # Case 1: For emails where order was not fully processed, price was not included
    # Assumptions: Assume company names will always be upper case (and may contain weird characters like -.:)
    matchString1 = r'Attached is an electronic confirmation confirming that we have (SOLD|BOUGHT) for you ([0-9]+) units in ([^a-z]+) at ([0-9.]+) '
    matchString2 = r'Attached is an electronic confirmation confirming that we have (SOLD|BOUGHT) for you ([0-9]+) units in ([^a-z]+) [a-z]+'
    if not re.search(matchString1, txtBody):
        print("! - Email body missing 'price' value, check email's pdf and enter 'stock price' specified")
        print("     Details of email with missing info in body:\n     - Date: {}\n     - Subject: {}\n".format(date, subject))
        if re.search(matchString2, txtBody):
            m = re.search(matchString2, txtBody)
            tradeType = m.group(1)
            units = m.group(2)
            companyName = m.group(3)

            correctTypeFlag = False
            while not correctTypeFlag:
                try:
                    price = float(input("     Enter price here: "))
                    correctTypeFlag = True
                except ValueError as e:
                    print("     !!! Warning !!! price entered was not a number, please try again")

                # Double check
                if correctTypeFlag:
                    confirm = input("     Confirm correct price is ${} per share? [y/n]: ".format(price))
                    if confirm != "y":
                        correctTypeFlag = False

        else:
            print("another unknown email format")
            print("Date: {}, Subject: {}".format(date, subject))
            exit()
    else:
        m = re.search(matchString1, txtBody)
        tradeType = m.group(1)
        units = m.group(2)
        companyName = m.group(3)
        price = m.group(4)

    # Store it in tradeTrack's tradeLogs
    tradeTrack.addToTradeLog(date, stockCode, companyName, tradeType, int(units), float(price))

    print("{}, {}, {}, {}, {}, {}".format(date, stockCode, companyName, tradeType, units, price))

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """

    # Check if there are cached trade logs

    # Get credentials
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    # Search for messages matching query which CommSec trade confirmation emails contain
    tradeTrack = tradeTracker.tradeTracker() # Module for tracking trades
    user_id = 'me' # For current authorised user
    messages = ListMessagesMatchingQuery(service, user_id, 'subject:equity trade confirmation')

    print("Num Emails matching trade confiration query: "+str(len(messages)))
    print("Processing email trade receipts")
    for message in messages:
        msg_id = message['id']
        mime_msg = GetMimeMessage(service, user_id, msg_id)
        processMimeMsgforTradeTrack(tradeTrack, mime_msg)
        
        exit() # TODO just for now


    # Capital gains/losses info
    # http://www.thebull.com.au/experts/a/277-how-do-you-calculate-capital-gains-and-losses-on-share-trades.html

if __name__ == '__main__':
    main()