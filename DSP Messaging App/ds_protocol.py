# Harshal Patel
# harshalp@uci.edu
# 93592684

import json
from collections import namedtuple
import time

"""
The ds_protocol module contains functions that support communication with the DSP Server.
"""


def get_sendmsg(token, message, recipient)->str:
    """Using the user token and message, returns a request following the correct protocol to communicate with the DSP
    server and request to send a direct message."""
    sendmsg = f'{{"token":"{token}", "directmessage": {{"entry": "{message}","recipient":"{recipient}", "timestamp": "{time.time()}"}}}}'
    #{"token":"{token}", "directmessage": {"entry": "Hello World!","recipient":"ohhimark", "timestamp":
    # "1603167689.3928561"}}
    return sendmsg

def get_sendmsg2(token, message, recipient)->str:
    """
    Using the user token and message, returns a request following the correct protocol to communicate with the DSP
    server and request to send a direct message. ————— This version is only for the test_ program. DO NOT USE OR DELETE
    """
    sendmsg = f'{{"token":"{token}", "directmessage": {{"entry": "{message}","recipient":"{recipient}"}}}}'
    #{"token":"{token}", "directmessage": {"entry": "Hello World!","recipient":"ohhimark", "timestamp":
    # "1603167689.3928561"}}
    return sendmsg



def get_msg_dict(message, recipient)->dict:
    """Using the message, recipient, and user's username, it creates a dictionary with the relevant information stored
    in the DirectMessage class and returns it."""
    sendmsg = {"recipient": recipient, "message": message, "timestamp": time.time()}

    return sendmsg


def get_rtrmsg(token, taip)->str:
    """Using the user token and type, returns a request following the correct protocol to communicate with the DSP
        server and request to retrieve messages sent to the user"""
    rtrmsg = f'{{"token":"{token}", "directmessage": "{taip}"}}'
    #{"token":"{token}", "directmessage": "new"}
    return rtrmsg


def get_joinmsg(username, password)->str:
    """Using the username and password, returns a request following the correct protocol to communicate with the DSP
        server and request join and exchange data."""
    joinmsg = f'{{"join": {{"username": "{username}","password": "{password}","token":""}}}}'
    return joinmsg


def load_srvmsg(srv_msg)->dict:
    """Loads the server's response from json into a python dictionary and returns it."""
    return json.loads(srv_msg)


def get_token(msg_dict):
    """Extracts the token from the dictionary of the server's response to the join request and returns it."""
    return msg_dict["response"]["token"]


def print_rMessage(msg_dict):
    """Extracts the response message from the dictionary of the server's response to the request and returns it."""
    try:
        # for responses to join and send requests.
        pass
        # print(msg_dict["response"]["message"])
    except KeyError:
        # for responses to retrieve requests
        if msg_dict["response"]["type"] == "ok":
            # print("Messages Successfully Retrieved.")
            pass


def get_responseType(msg_dict):
    """Extracts the response type from the dictionary of the server's response to the request and returns it."""
    return msg_dict["response"]["type"]


def incorrectlogin_response():
    """Prints the response for when an invalid username and/or password are entered"""
    print("Please try again with the correct username and password or create a new user!")


# The following functions are artifacts of the old ds_protocol from previous assignments ——————————————————————————————

# Namedtuple to hold the values retrieved from json messages.
# Actual JSON message: {"response": {"type": "ok", "message": "Bio published to DS Server"}}
DataTuple = namedtuple('DataTuple', ['type', 'message'])


def extract_json(json_msg: str) -> DataTuple:
    """
  Call the json.loads function on a json string and convert it to a DataTuple object

  DONE: replace the pseudo placeholder keys with actual DSP protocol keys
  """
    try:
        json_obj = json.loads(json_msg)
        rtype = json_obj["response"]['type']
        message = json_obj["response"]["message"]
        return DataTuple(rtype, message)
    except json.JSONDecodeError:
        print("Json cannot be decoded.")


def isolatepost(post):
    """Isolates the actual post from a post object."""
    return post["entry"]


def get_biomsg(token, bio)->str:
    """Using the user token and bio, returns a request following the correct protocol to communicate with the DSP
        server and request to add a new bio for the user, returning the server's response."""
    biomsg = f'{{"token":"{token}", "bio": {{"entry": "{bio}","timestamp": "{time.time()}"}}}}'
    return biomsg
