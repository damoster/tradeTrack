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

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """

    # Get credentials
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    # Search for messages matching query which CommSec trade confirmation emails contain
    user_id = 'me' # For current authorised user
    messages = ListMessagesMatchingQuery(service, user_id, 'subject:equity trade confirmation')
    print("Num Emails matching trade confiration query: "+str(len(messages)))
    for message in messages:
        msg_id = message['id']
        mime_msg = GetMimeMessage(service, user_id, msg_id)

        # print(mime_msg)
        date = mime_msg['Date']
        subject = mime_msg['Subject']
        txtBody = base64.urlsafe_b64decode(getTextBodyFromMimeMsg(mime_msg)).decode("utf-8")
        print("{}\n{}\n{}".format(date, subject, txtBody))
        exit()

        msgObj = service.users().messages().get(userId=user_id, id=msg_id, 
                                                format='full').execute() # full msg object fetch
        # for key in msgObj['payload']:
        #     print(key)
        print(msgObj['payload']['headers'])
        for headerKey in msgObj['payload']['headers']:
            print(headerKey)
        print("==========")

        # TODO later, check if multipart msg and turn into nice function similar to this
        # https://stackoverflow.com/questions/31967587/python-extract-the-body-from-a-mail-in-plain-text
        msg_str = msgObj['payload']['parts'][0]['body']['data']
        print(base64.urlsafe_b64decode(msg_str).decode("utf-8"))
        # Note only need to properly decode if want in utf-8 format
        # print(base64.urlsafe_b64decode(msg_str).decode("utf-8"))

        # msg_str = base64.urlsafe_b64decode(msgObj['raw'].encode('ASCII'))
        # mime_msg = email.message_from_string(msg_str)
        # print(mime_msg.get_payload())
        # print(msgObj['snippet'])
        # print("========")
        # print(msgObj['raw'].encode('ASCII'))
        exit() # TODO just for now

    # Capital gains/losses info
    # http://www.thebull.com.au/experts/a/277-how-do-you-calculate-capital-gains-and-losses-on-share-trades.html

if __name__ == '__main__':
    main()