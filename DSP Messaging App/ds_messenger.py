# Harshal Patel
# harshalp@uci.edu
# 93592684

import ds_protocol as dsp
import socket
import json


class DirectMessage(dict):
    """

    The Direct Message class stores all relevant information for a message in the following instance variables:

    - self.recipient: stores who is to receive the message of the message
    - self.message: stores the message itself
    - self.timestamp: stores the time that the message was sent
    - self.frm: stores who the message was sent by


    """

    def __init__(self, message: str = None, timestamp: float = 0, recipient: str = None, frm: str = None):
        self._message = message
        self._timestamp = timestamp
        self._recipient = recipient
        self._frm = frm

        self.set_timestamp(timestamp)
        self.set_message(message)
        self.set_recipient(recipient)
        self.set_frm(frm)

        # Subclass dict to expose Post properties for serialization
        # Don't worry about this!
        dict.__init__(self, message=self._message, timestamp=self._timestamp, recipient=self._recipient, frm=self._frm)

    def set_message(self, message):
        self._message = message
        dict.__setitem__(self, 'message', message)

    def set_recipient(self, recipient):
        self._recipient = recipient
        dict.__setitem__(self, 'recipient', recipient)

    def set_frm(self, frm):
        self._frm = frm
        dict.__setitem__(self, 'from', frm)

    def set_timestamp(self, timestamp):
        self._timestamp = float(timestamp)
        dict.__setitem__(self, 'timestamp', float(timestamp))

    def get_message(self):
        return self._message

    def get_time(self):
        return self._timestamp





class DirectMessenger:
    """
    The DirectMessenger class can be used to send and retrieve messages from the DSU server.

    It takes the following parameters upon initialization:

    :param username: The username to be assigned to the message.

    :param password: The password associated with the username

    *** Although the username and password parameters are "optional" and set to none, that's just how they were set in
    the starter code. I left them as is to avoid errors with the grading tool, but really they are mandatory and joining
    and sending and retrieving messages will only work successfully with a valid username and password pair. ***

    :param dsuserver: The IP address of the dsu server you would like to communicate with (default is set to the
    ICS 32 Distributed Social Website.

    :param port: The port used to connect to the server (default is set to the port used by the ICS 32 Distributed
     Social Website.

     DirectMessenger also saves all sent messages to the instance variable self.sent_messages as a List object.


    """

    def __init__(self, dsuserver="168.235.86.101", username=None, password=None, port=3021):
        self.token = None
        self.dsuserver = dsuserver
        self.port = port
        self.username = username
        self.password = password
        self.join_ok = False
        self.sent_messages = []

    def send(self, message, recipient) -> bool:
        """
        Takes a message (as a string) and recipient (as a string) and sends a message to the server requesting to send
         a message to the specified recipient.
        """

        server_response = self._communicate_w_server(server=self.dsuserver, port=self.port, taip="send",
                                                     message=message, recipient=recipient)

        # Checks to see if the message was successfully sent and returns the appropriate boolean
        # (true if message successfully sent, false if send failed.)

        if server_response["response"]["message"] == "Direct message sent":

            # saves the message that was successfully sent to the server
            msgdict = dsp.get_msg_dict(message=message, recipient=recipient)
            dm = DirectMessage(timestamp=msgdict["timestamp"], message=msgdict["message"], recipient=msgdict["recipient"], frm=self.username)
            # dm.fill_info_sent(messagedict=messagedict, myusername=self.username)
            self.sent_messages.append(dm)

            return True
        else:
            return False

    def retrieve_new(self) -> list:
        """
        returns a list of DirectMessage objects containing all new messages
        """

        server_response = self._communicate_w_server(server=self.dsuserver, port=self.port, taip="new")

        messages = server_response["response"]["messages"]
        messagelist = []
        for message in messages:
            newmessage = DirectMessage(timestamp=message["timestamp"], message=message["message"], recipient=self.username, frm=message["from"])
            # newmessage.fill_info_received(message, self.username)
            messagelist.append(newmessage)

        return messagelist

    def retrieve_all(self) -> list:
        """
        returns a list of DirectMessage objects containing all messages
        """
        server_response = self._communicate_w_server(server=self.dsuserver, port=self.port, taip="all")

        messages = server_response["response"]["messages"]
        messagelist = []
        for message in messages:
            newmessage = DirectMessage(timestamp=message["timestamp"], message=message["message"], recipient=self.username, frm=message["from"])
            # newmessage.fill_info_received(message, self.username)
            messagelist.append(newmessage)

        return messagelist

    def _communicate_w_server(self, server: str, port: int, taip: str, message=str,
                              recipient=str):
        """
    The send function joins a ds server and sends a message, bio, or both

    :param server: The ip address for the ICS 32 DS server.
    :param port: The port where the ICS 32 DS server is accepting connections.
    :param taip: The type of communication wanted -- "send" to send a direct message,"new" to retrieve new messages,
                 or "all" to retrieve all received messages.
    :param message: the direct message you wish to send
    :param recipient: the username of the user you want to send a message to.

    """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((server, port))
                joinresponse = self._send_to_server(client=client, username=self.username, password=self.password,
                                                    typ="join")

                if dsp.get_responseType(joinresponse) == "ok":
                    token = dsp.get_token(joinresponse)
                    self.token = token
                    self.join_ok = True

                    if taip == "send":
                        if self.join_ok:
                            server_response = self._send_to_server(client=client, token=token, message=message,
                                                                   recipient=recipient, typ=taip)

                    else:
                        server_response = self._send_to_server(client=client, token=token, typ=taip)

                else:
                    dsp.incorrectlogin_response()
        except socket.gaierror:
            print("Unable to connect to server, please try again with a valid IP address and Port number!")

        return server_response

    def _send_to_server(self, client, username=None, password=None, token=None, message=None, recipient=None, typ=None):

        """Sends a join message to connect and retrieve a token for the requested account."""

        join_send = client.makefile('w')
        join_recv = client.makefile('r')

        # print("client connected to {HOST} on {PORT}")
        # print()
        if typ == "join":
            msg = dsp.get_joinmsg(username, password)
        elif typ == "send":
            msg = dsp.get_sendmsg(token, message, recipient)
        else:
            msg = dsp.get_rtrmsg(token, typ)

        join_send.write(msg + '\r\n')
        join_send.flush()
        srv_msg = join_recv.readline()
        msg_dict = dsp.load_srvmsg(srv_msg)
        # print(srv_msg)
        dsp.print_rMessage(msg_dict)

        return msg_dict
