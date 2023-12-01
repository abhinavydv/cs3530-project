import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from socket import socket, AF_INET, SOCK_DGRAM


class TextEditWindow(Gtk.Window):
    def __init__(self, parent):
        super().__init__(title="Text Editor", transient_for=parent, modal=True)

        self.curr_file = None
        self.IP = self.getIP()

        self.set_default_size(650, 350)
        self.grid = Gtk.Grid()

        self.add(self.grid)

        self.create_textview()
        self.create_menubar()
        
    def getIP(self):
        """
            Get the IP address of the current host
        """
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("10.255.255.255", 1234))
        return s.getsockname()[0]

    def create_textview(self):
        """
            Create a textview and add it to the grid
        """
        sw = Gtk.ScrolledWindow()
        sw.set_hexpand(True)
        sw.set_vexpand(True)
        self.grid.attach(sw, 0, 1, 1, 1)

        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text("This is some text inside of a Gtk.TextView. "
                                 + "Select text and click one of the buttons 'bold', 'italic', "
                                 + "or 'underline' to modify the text accordingly.")

        sw.add(self.textview)

    def create_menubar(self):
        """
            Create a menubar and add it to the grid
        """
        menu_bar = Gtk.MenuBar()
        self.grid.attach(menu_bar, 0, 0, 1, 1)
        
        file_menu = Gtk.Menu()
        file_menu_item = Gtk.MenuItem(label="File")

        file_menu_item.set_submenu(file_menu)
        menu_bar.append(file_menu_item)

        new_file_item = Gtk.MenuItem(label="New")
        file_menu.append(new_file_item)
        new_file_item.connect("activate", self.new_file)

        open_file_item = Gtk.MenuItem(label="Open")
        file_menu.append(open_file_item)
        open_file_item.connect("activate", self.open_file)
        
        share_file_item = Gtk.MenuItem(label="Share")
        file_menu.append(share_file_item)
        share_file_item.connect("activate", self.share_file)

        connect_file_item = Gtk.MenuItem(label="Connect")
        file_menu.append(connect_file_item)
        connect_file_item.connect("activate", self.connect_file)

        exit_file_item = Gtk.MenuItem(label="Exit")
        file_menu.append(exit_file_item)
        exit_file_item.connect("activate", self.exit_app)

    def new_file(self, _):
        """
            Create a new file
        """
        self.file_dialog = Gtk.FileChooserDialog(
            title="Choose a file", parent=self, action=Gtk.FileChooserAction.SAVE
        )
        
        self.file_dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Create File", Gtk.ResponseType.OK
        )

        self.response = self.file_dialog.run()

        if self.response == Gtk.ResponseType.OK:
            self.file_name = self.file_dialog.get_filename()
            self.file = open(self.file_name, "w")
            self.textbuffer.set_text("")
            self.file.close()

        elif self.response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        self.file_dialog.destroy()

    def open_file(self, _):
        """
            Open a file
        """
        self.file_dialog = Gtk.FileChooserDialog(
            title="Choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )

        self.file_dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Open File", Gtk.ResponseType.OK
        )

        self.response = self.file_dialog.run()

        if self.response == Gtk.ResponseType.OK:
            self.file_name = self.file_dialog.get_filename()
            self.file = open(self.file_name, "r")
            self.contents = self.file.read()
            self.textbuffer.set_text(self.contents)
            self.file.close()

        elif self.response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        self.file_dialog.destroy()

    def connect_file(self, _):
        """
            Take link as input and connect to a host
        """
        self.input_dialog = Gtk.Dialog(
            title="Connect to a host", parent=self, modal=True
        )
        self.input_dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Connect", Gtk.ResponseType.OK
        )

        box = self.input_dialog.get_content_area()
        label = Gtk.Label(label="Insert link to connect to a host:")

        box.add(label)
        self.entry = Gtk.Entry()
        box.add(self.entry)

        self.input_dialog.show_all()

        self.response = self.input_dialog.run()

        if self.response == Gtk.ResponseType.OK:
            self.link = self.entry.get_text()
            print(self.link)
        else:
            pass

        self.input_dialog.destroy()

    def generate_link(self):
        """
            Generate a link to share the file
        """

    def share_file(self, _):
        """
            Share a file
        """
        link = self.generate_link()

    def exit_app(self, _):
        """
            Exit the application
        """
        Gtk.main_quit()

    def insert_text(self, pos, text):
        """
            Insert text at the given position
        """


if __name__ == "__main__":
    win = TextEditWindow(None)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
