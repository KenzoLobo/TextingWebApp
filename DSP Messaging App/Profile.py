# EDITED NOW


# Profile.py
#
# ICS 32 Fall 2021
# Assignment #2: Journal
#
# Author: Mark S. Baldwin
#
# v0.1.7

# You should review this code to identify what features you need to support
# in your program for assignment 2.
#
# YOU DO NOT NEED TO READ OR UNDERSTAND THE JSON SERIALIZATION ASPECTS OF THIS CODE RIGHT NOW, 
# though can you certainly take a look at it if you are curious.
#
import json, time, os
from pathlib import Path
from ds_messenger import DirectMessage

"""
DsuFileError is a custom exception handler that you should catch in your own code. It
is raised when attempting to load or save Profile objects to file the system.

"""


class DsuFileError(Exception):
    pass


"""
DsuProfileError is a custom exception handler that you should catch in your own code. It
is raised when attempting to deserialize a dsu file to a Profile object.

"""


class DsuProfileError(Exception):
    pass


class Post(dict):
    """ 

    The Post class is responsible for working with individual user posts. It currently supports two features: 
    A timestamp property that is set upon instantiation and when the entry object is set and an 
    entry property that stores the post message.

    """

    def __init__(self, entry: str = None, timestamp: float = 0):
        self._timestamp = timestamp
        self.set_entry(entry)

        # Subclass dict to expose Post properties for serialization
        # Don't worry about this!
        dict.__init__(self, entry=self._entry, timestamp=self._timestamp)

    def set_entry(self, entry):
        self._entry = entry
        dict.__setitem__(self, 'entry', entry)

        # If timestamp has not been set, generate a new from time module
        if self._timestamp == 0:
            self._timestamp = time.time()

    def get_entry(self):
        return self._entry

    def set_time(self, time: float):
        self._timestamp = time
        dict.__setitem__(self, 'timestamp', time)

    def get_time(self):
        return self._timestamp

    """

    The property method is used to support get and set capability for entry and time values.
    When the value for entry is changed, or set, the timestamp field is updated to the
    current time.

    """
    entry = property(get_entry, set_entry)
    timestamp = property(get_time, set_time)


class Profile:
    """
    The Profile class exposes the properties required to join an ICS 32 DSU server. You will need to 
    use this class to manage the information provided by each new user created within your program for a2. 
    Pay close attention to the properties and functions in this class as you will need to make use of 
    each of them in your program.

    When creating your program you will need to collect user input for the properties exposed by this class. 
    A Profile class should ensure that a username and password are set, but contains no conventions to do so. 
    You should make sure that your code verifies that required properties are set.

    """

    def __init__(self, dsuserver=None, username=None, password=None):
        self.dsuserver = dsuserver  # REQUIRED
        self.username = username  # REQUIRED
        self.password = password  # REQUIRED
        self.bio = ''  # OPTIONAL
        self._posts = []  # OPTIONAL

        self._messages = []

        self._users = []  # This list used to store the usernames of users that you have messages with

    #  Done: Write a function that goes through all the messages and returns a list of all the posts to/from a specific
    #   user. You should be able to enter a username into the function as a parameter and get a list of all their
    #   sent/received messages.

    def get_chat_messages(self, username: str) -> list:
        """
        accepts a username and returns a list of all the messages in the chat with that user
        """

        chat_messages = []

        for message in self._messages:
            if (message['from'] == username or message['recipient'] == username):
                chat_messages.append(message)

        return chat_messages

    def add_post(self, post: Post) -> None:
        """

        add_post accepts a Post object as parameter and appends it to the posts list. Posts are stored in a
        list object in the order they are added. So if multiple Posts objects are created, but added to the
        Profile in a different order, it is possible for the list to not be sorted by the Post.timestamp property.
        So take caution as to how you implement your add_post code.

        """
        self._posts.append(post)

    def add_msg(self, message: DirectMessage) -> None:
        """

        add_msg accepts a DirectMessage object as parameter and appends it to the messages list.

        """
        # Done: Add code that checks both the frm and recipient instances of the message and adds the username to the
        #  self._users variable IF the username is NOT self.username AND is NOT already on the list.
        message_recipient = message['recipient']
        message_from = message['from']

        message_recipient_exists = False
        message_from_exists = False

        for usr in self._users:
            if usr == message_recipient:
                message_recipient_exists = True
            if usr == message_from:
                message_from_exists = True

        if message_recipient_exists == False and message_recipient != self.username:
            self._users.append(message_recipient)
        if message_from_exists == False and message_from != self.username:
            self._users.append(message_from)

        self._messages.append(message)

    def del_post(self, index: int) -> bool:
        """

        del_post removes a Post at a given index and returns True if successful and False if an invalid
        index was supplied.

        To determine which post to delete you must implement your own search operation on the posts
        returned from the get_posts function to find the correct index.

        """
        try:
            del self._posts[index]
            return True
        except IndexError:
            return False

    def get_posts(self) -> list:
        """

        get_posts returns the list object containing all posts that have been added to the Profile object

        """
        return self._posts

    def save_profile(self, path: str) -> None:
        """

        save_profile accepts an existing dsu file to save the current instance of Profile to the file system.

        Example usage:

        profile = Profile()
        profile.save_profile('/path/to/file.dsu')

        Raises DsuFileError

        """

        # Done: Use the function that creates the dictionary of conversations

        p = Path(path)

        if os.path.exists(p) and p.suffix == '.dsu':
            try:
                f = open(p, 'w')
                json.dump(self.__dict__, f)
                f.close()
            except Exception as ex:
                raise DsuFileError("An error occurred while attempting to process the DSU file.", ex)
        else:
            raise DsuFileError("Invalid DSU file path or type")

    def load_profile(self, path: str) -> None:
        """

        load_profile will populate the current instance of Profile with data stored in a DSU file.

        Example usage:

        profile = Profile()
        profile.load_profile('/path/to/file.dsu')

        Raises DsuProfileError, DsuFileError

        """
        p = Path(path)

        if os.path.exists(p) and p.suffix == '.dsu':
            try:
                f = open(p, 'r')
                obj = json.load(f)
                self.username = obj['username']
                self.password = obj['password']
                self.dsuserver = obj['dsuserver']
                self.bio = obj['bio']
                for post_obj in obj['_posts']:
                    post = Post(post_obj['entry'], post_obj['timestamp'])
                    self._posts.append(post)
                for message in obj['_messages']:
                    msg = DirectMessage(message=message["message"], timestamp=message["timestamp"],
                                        recipient=message["recipient"], frm=message["frm"])
                    self._messages.append(msg)
                for user in obj['_users']:
                    self._users.append(user)
                f.close()
            except Exception as ex:
                raise DsuProfileError(ex)
        else:
            raise DsuFileError()
