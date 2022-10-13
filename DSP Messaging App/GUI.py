# A GUI to facilitate a graphical means to send and recieve messages from
# the DSP server

# Hayden Powers
# powersh@uci.edu
# 56169764

import tkinter as tk
from tkinter import ttk, filedialog, TclError
from Profile import Post, Profile
from ds_messenger import DirectMessenger, DirectMessage
import copy


class Body(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets
    in the body portion of the root frame.
    """

    def __init__(self, root, select_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._select_callback = select_callback

        # the currently active profile
        self.current_profile = Profile()
        self.current_path = ""

        # a list of the messages available in the active DSU file
        self._messages = []

        # A list of usernames that the current profile has sent/recieved messages
        self._contacts = []

        # This is a variable to be set by node select when clicked on a particular
        # contact, is accessed in order to send to correct recipient
        self.selected_contact = ''

        # This is what will be tied to each username so that when a contact is clicked on the
        # TreeView widget, it will display the chat history
        self._chat_history = []

        # After all initialization is complete, call the _draw method to pack the widgets
        # into the Body instance 
        self._draw()

    def generate_chat_history(self, messages):
        """
        This function will take the sent messages from the user and recieved messages from other
        users and combine them chronologically into ._chat_history and prints to message view in a
        friendly format
        """
        sorted_list = self.sort_by_timestamp(messages)

        for element in sorted_list:
            username_frm = element['frm']
            message = element['message']
            formatted = f"{username_frm} : {message} \n\n"

            if formatted not in self._chat_history:
                self._chat_history.append(formatted)

    def sort_by_timestamp(self, message_list):
        """
        This function takes a list of messages and sorts it by timestamp.
        """
        sorted_list = sorted(message_list, key=lambda d: d['timestamp'])
        return sorted_list


    def node_select(self, event):
        """
        Nodes will have the username of all the accounts that you have sent/recieved messages to.
        Clicking on a node will open the chat history (sent and recieved messages in chronologial order)
        """
        digits = self.posts_tree.selection()[0][1:]
        leading_zeros = True
        value = ''

        # The .selection()[0] method of our treeview widget returns a 4 character string as an id
        # here I just got rid of the leading zeroes and got an accurate index value by converting
        # it from hexadecimal
        for i in digits:
            if i == '0' and leading_zeros:
                continue
            elif i != '0':
                leading_zeros = False
            value = value + i

        index = int(value, 16) - 1

        self.selected_contact = self._contacts[index]
        self.current_profile.load_profile(self.current_path)

        self._chat_history = []

        contact_messages = self.current_profile.get_chat_messages(self.selected_contact)
        self.generate_chat_history(contact_messages)

        print(self._chat_history)
        self.message_viewer.delete(0.0, "end")

        for chat in self._chat_history:
            self.message_viewer.insert(0.0, chat)

        print("CURENT CONTACT SELECTED: ", self.selected_contact)


    def get_text_entry(self) -> str:
        """
        Returns the text that is currently displayed in the message_editor widget.
        """
        return self.message_editor.get('1.0', 'end').rstrip()

    def set_text_entry(self, text: str):
        """
        Sets the text to be displayed in the message_viewer widget.
        """
        self.message_viewer.delete(0.0, "end")
        self.message_viewer.insert(0.0, text)

    def set_messages(self, messages: list):
        """
        Populates the self._messages attribute with messages from the active DSU file.
        """
        self._messages = copy.deepcopy(messages)

    def set_contacts(self, users: list):
        """
        Populates the ._contacts attribute with the users from the acive DSU file
        """
        self._contacts = copy.deepcopy(users)
        for contact in self._contacts:
            try:
                self._insert_post_tree(len(self._messages), contact)
            except TclError as e:
                print("set_contacts error")
                continue

    def add_contact(self, username: str):
        """
        Adds an individual contact to the list of contacts.
        """
        self._contacts.append(username)
        try:
            self._insert_post_tree(len(self._messages), username)
        except TclError as e:
            print("add_contacts error")
            return

    def insert_post(self, message: dict):
        """
        Inserts a single post to the post_tree widget.
        """
        self._messages.append(dict)
        id = len(self._messages) - 1  # adjust id for 0-base of treeview widget
        self._insert_post_tree(id, message)

    def get_contacts(self):
        """
        Get list of current contacts for current profile in main app in order to save to dsu file
        """

        return self._contacts

    def reset_ui(self):
        """
        Resets all UI widgets to their default state. Useful for when clearing the UI is neccessary such
        as when a new DSU file is loaded, for example.
        """
        self.set_text_entry("")
        self.message_editor.configure(state=tk.NORMAL)
        self._messages = []
        for item in self.posts_tree.get_children():
            self.posts_tree.delete(item)

    def _insert_post_tree(self, id, contact):
        """
        Inserts a post entry into the posts_tree widget.
        """
        # Title for messages in message tree will be the username of the 'frm' variable
        self.posts_tree.insert('', id, text=contact)


    def update_messages(self):
        """
        This function will run on a timer to check for incoming messages to the user and update the profile and GUI
        accordingly.
        """
        current_user = Profile()
        current_user.load_profile(self.current_path)
        update_messenger = DirectMessenger(username=current_user.username, password=current_user.password)
        newmessages = update_messenger.retrieve_new()

        for message in newmessages:
            if message not in current_user._messages:
                current_user.add_msg(message)

        current_user.save_profile(self.current_path)

        if self.selected_contact != '':
            contact_messages = current_user.get_chat_messages(self.selected_contact)
            self.generate_chat_history(contact_messages)

            for chat in self._chat_history:
                if chat not in self.message_viewer.get('1.0', 'end'):
                    self.message_viewer.insert(0.0, chat)

        tree_contact_list = []

        for i in self.posts_tree.get_children():
            tree_contact_list.append(self.posts_tree.item(i)["text"])
        for user in current_user._users:
            if user not in tree_contact_list:
                self.add_contact(user)
        # print("looping")
        self.root.after(ms=1000, func=self.update_messages)

    def _draw(self):
        """
        Call only once upon initialization to add widgets to the frame
        """
        posts_frame = tk.Frame(master=self, width=250)
        posts_frame.pack(fill=tk.BOTH, side=tk.LEFT)
        self.posts_tree = ttk.Treeview(posts_frame)
        self.posts_tree.bind("<<TreeviewSelect>>", self.node_select)
        self.posts_tree.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=5, pady=5)

        entry_frame = tk.Frame(master=self, bg="green")
        entry_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

        # NEW FRAMES ------
        view_frame = tk.Frame(master=entry_frame, bg="orange")
        view_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

        viewer_scroll_frame = tk.Frame(master=view_frame, bg="yellow", width=10)
        viewer_scroll_frame.pack(fill=tk.BOTH, side=tk.RIGHT, expand=False)

        message_frame = tk.Frame(master=entry_frame, bg="blue")
        message_frame.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True)

        editor_scroll_frame = tk.Frame(master=message_frame, bg="red", width=10)
        editor_scroll_frame.pack(fill=tk.BOTH, side=tk.RIGHT, expand=False)
        # -----------------

        # NEW WIDGETS ------
        self.message_viewer = tk.Text(master=view_frame, height=20, width=0)
        self.message_viewer.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=1, pady=1)

        self.message_editor = tk.Text(master=message_frame, height=10, width=0)
        self.message_editor.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

        message_viewer_scrollbar = tk.Scrollbar(master=viewer_scroll_frame, command=self.message_viewer.yview)
        self.message_viewer['yscrollcommand'] = message_viewer_scrollbar.set
        message_viewer_scrollbar.pack(fill=tk.Y, side=tk.LEFT, expand=False, padx=0, pady=0)

        message_editor_scrollbar = tk.Scrollbar(master=editor_scroll_frame, command=self.message_editor.yview)
        self.message_editor['yscrollcommand'] = message_editor_scrollbar.set
        message_editor_scrollbar.pack(fill=tk.Y, side=tk.LEFT, expand=False, padx=0, pady=0)
        # ----------------------------------------------

class Footer(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets
    in the footer portion of the root frame.
    """
    def __init__(self, root, send_callback=None, add_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._send_callback = send_callback
        self._add_callback = add_callback

        # IntVar is a variable class that provides access to special variables
        # for Tkinter widgets. is_online is used to hold the state of the chk_button widget.
        # The value assigned to is_online when the chk_button widget is changed by the user
        # can be retrieved using he get() function:
        # chk_value = self.is_online.get()
        self.is_online = tk.IntVar()
        # After all initialization is complete, call the _draw method to pack the widgets
        # into the Footer instance 
        self._draw()

    def add_click(self):
        """
        Calls the callback function specified in the online_callback class attribute, if
        available, when the chk_button widget has been clicked.
        """
        if self._add_callback is not None:
            self._add_callback()

    def send_click(self):
        """
        Calls the callback function specified in the save_callback class attribute, if
        available, when the save_button has been clicked.
        """
        if self._send_callback is not None:
            self._send_callback()

    def _draw(self):
        """
        Call only once upon initialization to add widgets to the frame
        """
        send_button = tk.Button(master=self, text="Send Message", width=20)
        send_button.configure(command=self.send_click)
        send_button.pack(fill=tk.BOTH, side=tk.RIGHT, padx=5, pady=5)

        # ADD USER BUTTON INSTEAD OF READY LABEL
        add_user_button = tk.Button(master=self, text="Add User", width=10)
        add_user_button.configure(command=self.add_click)
        add_user_button.pack(fill=tk.BOTH, side=tk.LEFT, padx=10, pady=5)


class MainApp(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets
    in the main portion of the root frame. Also manages all method calls for
    the Profile class.
    """
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root

        # Initialize a new Profile and assign it to a class attribute.
        self._current_profile = Profile()

        # To make sure that a file is open before using send/add
        self._profile_filename = False

        # After all initialization is complete, call the _draw method to pack the widgets
        # into the root frame
        self._draw()

    def send_message(self):
        """
        Takes the message from the message editor and sends it through the DSP server
        to the specified username
        """
        # May need to plan this to accept an index from a contacts list instead of
        # passing in a username. 
        message = self.body.get_text_entry()
        self.body.message_editor.delete(0.0, "end")
        dm_user = DirectMessenger(username=self._current_profile.username,
                                  password=self._current_profile.password)

        dm_user.send(message, self.body.selected_contact)

        currentprofile = Profile()
        if self._profile_filename is not False:
            currentprofile.load_profile(self._profile_filename)
            currentprofile.add_msg(dm_user.sent_messages[0])
            currentprofile.save_profile(self._profile_filename)
        print("MESSAGE SENT")

    def new_profile(self):
        """
        Creates a new DSU file when the 'New' menu item is clicked.
        """
        if self._profile_filename == False:
            filename = tk.filedialog.asksaveasfile(filetypes=[('Distributed Social Profile', '*.dsu')],
                                                   defaultextension='.dsu')
            try:
                self._profile_filename = filename.name
                self._current_profile = Profile()
                self.body.reset_ui()
                self.body.set_contacts(self._current_profile._users)
                self.body.current_profile = self._current_profile
                self.body.current_path = self._profile_filename
            except AttributeError as e:
                print("New profile operation interrupted.")

            # Opens a new popup window for user to enter their own username and password
            if self._profile_filename is False:
                print("No filename provided")
                return
            else:
                self.newfile_window()
        else:
            print("Please restart the program before trying to create a new profile.")

    def newfile_window(self):
        """
        A popup window that will prompt the user for username and password when creating a new file
        """
        self.newfile_popup = tk.Toplevel()

        user_label = tk.Label(master=self.newfile_popup, text="Username")
        user_label.pack(fill='x', padx=50, pady=5)
        self.user_input = tk.Text(master=self.newfile_popup, height=1, width=20)
        self.user_input.pack(fill='x', padx=50, pady=5)

        password_label = tk.Label(master=self.newfile_popup, text="Password")
        password_label.pack(fill='x', padx=50, pady=5)
        self.password_input = tk.Text(master=self.newfile_popup, height=1, width=20)
        self.password_input.pack(fill='x', padx=50, pady=5)

        button_submit = tk.Button(master=self.newfile_popup, text="Submit", width=5, command=lambda: self.submit_info())
        button_submit.pack(fill='x')

    # vvvv-------------------ADDED AFTER HARSHAL GUI---------------------vvvvv

    def add_user_window(self):
        """
        A popup window that will prompt the user for username to add to contacts list
        """
        self.add_popup = tk.Toplevel()

        contact_label = tk.Label(master=self.add_popup, text="Recipient Username:")
        contact_label.pack(fill='x', padx=50, pady=5)
        self.contact_input = tk.Text(master=self.add_popup, height=1, width=20)
        self.contact_input.pack(fill='x', padx=50, pady=5)

        add_contact = tk.Button(master=self.add_popup, text="Add Contact", width=5, command=lambda: self.add_user())
        add_contact.pack(fill='x')

    def submit_info(self):
        """
        The command used by the submit button in the popup window to set the current profile username
        and password and save profile to the dsu file
        """
        self._current_profile.username = self.user_input.get("1.0", 'end-1c')
        self._current_profile.password = self.password_input.get("1.0", 'end-1c')

        messenger = DirectMessenger(username=self._current_profile.username, password=self._current_profile.password)
        username_valid = True
        try:
            messenger.retrieve_all()
        except UnboundLocalError:
            self._current_profile.username = "dusername123"
            self._current_profile.password = "dpassword123"

        self._current_profile.save_profile(self._profile_filename)
        self.body.update_messages()
        self.newfile_popup.destroy()

    def add_user(self):
        """
        A callback function for responding to the add_user button. Will connect with the body
        to insert an empty chat history with a given username supplied by the message editor
        """
        if self._profile_filename is False:
            print("No filename provided.")
            return

        self._current_profile.load_profile(self._profile_filename)  # Load first
        contact = self.contact_input.get("1.0", 'end-1c')

        # If contact is nothing, do not add
        if contact == '':
            return
        elif contact not in self.body._contacts:
            self.body.add_contact(contact)
            self._current_profile._users = self.body.get_contacts()

            print("CURRENT USERS from MAINAPP: ", self._current_profile._users)

        else:
            print("Contact already exists.")

        self._current_profile.save_profile(self._profile_filename)  # Save last
        self.add_popup.destroy()

    def open_profile(self):
        """
        Opens an existing DSU file when the 'Open' menu item is clicked and loads the profile
        data into the UI.
        """
        if self._profile_filename == False:
            filename = tk.filedialog.askopenfile(filetypes=[('Distributed Social Profile', '*.dsu')])
            try:
                self._profile_filename = filename.name
                self._current_profile = Profile()
                self._current_profile.load_profile(self._profile_filename)
                self.body.reset_ui()  # Reset UI
                # self.body.set_messages(self._current_profile._messages)
                self.body.set_contacts(self._current_profile._users)
                self.body.current_profile = self._current_profile
                self.body.current_path = self._profile_filename

                # UPDATE MESSAGES HERE
                self.body.update_messages()

            except AttributeError as e:
                print("Open operation interrupted.")
        else:
            print("Please restart the program before loading a new profile!")

    def close(self):
        """
        Closes the program when the 'Close' menu item is clicked.
        """
        self.root.destroy()

    def save_profile(self):
        """
        Saves the text currently in the message_editor widget to the active DSU file.
        """
        # Check for filename
        if self._profile_filename is False:
            print("No filename provided")
            return

    def _draw(self):
        """
        Call only once, upon initialization to add widgets to root frame
        """
        # Build a menu and add it to the root frame.
        menu_bar = tk.Menu(self.root)
        self.root['menu'] = menu_bar
        menu_file = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='New', command=self.new_profile)
        menu_file.add_command(label='Open...', command=self.open_profile)
        menu_file.add_command(label='Close', command=self.close)

        # The Body and Footer classes must be initialized and packed into the root window.
        self.body = Body(self.root, self._current_profile)
        self.body.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self.footer = Footer(self.root, send_callback=self.send_message, add_callback=self.add_user_window)
        self.footer.pack(fill=tk.BOTH, side=tk.BOTTOM)


if __name__ == "__main__":
    # All Tkinter programs start with a root window. We will name ours 'main'.
    main = tk.Tk()

    # 'title' assigns a text value to the Title Bar area of a window.
    main.title("ICS 32 Distributed Social Demo")

    # This is just an arbitrary starting point. You can change the value around to see how
    # the starting size of the window changes. I just thought this looked good for our UI.
    main.geometry("720x480")

    # adding this option removes some legacy behavior with menus that modern OSes don't support. 
    # If you're curious, feel free to comment out and see how the menu changes.
    main.option_add('*tearOff', False)

    # Initialize the MainApp class, which is the starting point for the widgets used in the program.
    # All of the classes that we use, subclass Tk.Frame, since our root frame is main, we initialize 
    # the class with it.
    MainApp(main)

    # When update is called, we finalize the states of all widgets that have been configured within the root frame.
    # Here, Update ensures that we get an accurate width and height reading based on the types of widgets
    # we have used.
    # minsize prevents the root window from resizing too small. Feel free to comment it out and see how
    # the resizing behavior of the window changes.
    main.update()
    main.minsize(main.winfo_width(), main.winfo_height())
    # And finally, start up the event loop for the program (more on this in lecture).
    main.mainloop()
