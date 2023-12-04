import gi
import uuid
import hashlib
from time import sleep
from queue import Queue
from control.control_layer import ControlLayer
from consistency.crdt_final import CRDT
import string


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,GLib,Gdk

from socket import socket, AF_INET, SOCK_DGRAM


class TextEditWindow(Gtk.Window):
    def __init__(self, parent):
        super().__init__(title="Text Editor", transient_for=parent, modal=True)

        self.running = True

        self.file_name = None
        self.link = None
        self.uuid = uuid.getnode().to_bytes(6, "little")
        self.crdt = None
        self.cl = None
        self.counter = 0
        self.IP = self.getIP()
        self.port = 11419
        self.queue = Queue()
        self.update_queue = Queue()
        self.last_written = 0

        self.mouse_clicked = False

        self.last_cursor_pos = 0

        self.timeout = GLib.timeout_add(1000, self.on_timeout)
        self.queue_timeout = GLib.timeout_add(100, self.on_queue_timeout)
        self.set_default_size(650, 350)
        self.grid = Gtk.Grid()

        self.add(self.grid)

        self.create_menubar()
        self.create_textview()

        self.printable = list(map(ord, string.printable))

    def getIP(self):
        """
            Get the IP address of the current host
        """
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("10.43.45.3", 1234))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def get_cur_pos(self):
        """
            Get the current cursor position
        """
        return self.textbuffer.get_property('cursor-position')

    def create_textview(self):
        """
            Create a textview and add it to the grid
        """
        sw = Gtk.ScrolledWindow()
        sw.set_hexpand(True)
        sw.set_vexpand(True)
        self.grid.attach(sw, 0, 1, 1, 1)

        self.textview = Gtk.TextView()
        self.textview.connect("key-release-event", self.on_key_press_event)
        self.textview.connect("button-press-event", self.on_mouse_button_press)

        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview.set_sensitive(False)
        self.textbuffer = self.textview.get_buffer()
        # self.textbuffer.set_text("This is some text inside of a Gtk.TextView. "
        #                          + "Select text and click one of the buttons 'bold', 'italic', "
        #                          + "or 'underline' to modify the text accordingly.")

        sw.add(self.textview)

    def on_mouse_button_press(self, widget, event):
        print("mouse button pressed")
        self.on_timeout()
        self.mouse_clicked = True
        self.last_written = self.textbuffer.get_property('cursor-position')
        print(self.last_written)

    def on_key_press_event(self,widget,event,*args):
        # if self.mouse_clicked:
        #     self.mouse_clicked = False
        #     self.last_written = self.textbuffer.get_property('cursor-position')

        cursor_position = self.textbuffer.get_property('cursor-position')
        # self.counter = cursor_position - self.last_written

        if Gdk.keyval_name(event.keyval) == 'BackSpace':
            self.on_timeout()
            data = [1, self.last_written-1, self.last_written]
            print("putting data 1")
            self.queue.put(data)
            # self.last_written = cursor_position
            self.last_written -= 1
            GLib.source_remove(self.timeout)
            self.timeout = GLib.timeout_add(100, self.on_timeout)
            return 

        if Gdk.keyval_name(event.keyval) in ['Left','Right','Up','Down']:
            self.on_timeout()
            self.last_written = cursor_position
            return

        print("key: ", Gdk.keyval_name(event.keyval))
        print(Gdk.keyval_to_unicode(event.keyval))
        if Gdk.keyval_to_unicode(event.keyval) in self.printable + [ord(i) for i in ' \n\t']:
            self.counter += 1
        if (self.counter > 2):
            # text = self.textbuffer.get_text(self.textbuffer.get_iter_at_offset(self.last_written), self.textbuffer.get_iter_at_offset(self.last_written+self.counter), True)
            # data = [0,self.last_written,text]
            # print("putting data 2")
            # self.queue.put(data)
            # self.last_written += self.counter
            # # self.last_written = cursor_position
            # self.counter = 0
            # GLib.source_remove(self.timeout)
            # self.timeout = GLib.timeout_add(1000, self.on_timeout)
            self.on_timeout()
            return


    def on_timeout(self, data=None):
        if data is None:
            text = self.textbuffer.get_text(self.textbuffer.get_iter_at_offset(self.last_written), self.textbuffer.get_iter_at_offset(self.last_written+self.counter), True)
            data = [0, self.last_written, text]
        # data = [0, self.last_written,self.textbuffer.get_text(self.textbuffer.get_iter_at_offset(self.last_written), self.textbuffer.get_iter_at_offset(self.last_written+self.counter), True)]
        if (data[2] != ""):
            print("putting data 3")
            self.queue.put(data)
        self.last_written += self.counter
        # self.last_written = self.textbuffer.get_property('cursor-position')
        self.counter = 0

        GLib.source_remove(self.timeout)
        if self.running:
            self.timeout = GLib.timeout_add(100, self.on_timeout)

    def on_queue_timeout(self):
        if not self.update_queue.empty():
            self.update_text(*self.update_queue.get())
        GLib.source_remove(self.queue_timeout)
        if self.running:
            self.queue_timeout = GLib.timeout_add(100, self.on_queue_timeout)

    def create_menubar(self):
        """
            Create a menubar and add it to the grid
        """
        self.menu_bar = Gtk.MenuBar()
        self.grid.attach(self.menu_bar, 0, 0, 1, 1)

        self.file_menu = Gtk.Menu()
        self.file_menu_item = Gtk.MenuItem(label="File")

        self.file_menu_item.set_submenu(self.file_menu)
        self.menu_bar.append(self.file_menu_item)

        self.new_file_item = Gtk.MenuItem(label="New")
        self.file_menu.append(self.new_file_item)
        self.new_file_item.connect("activate", self.new_file)

        self.open_file_item = Gtk.MenuItem(label="Open")
        self.file_menu.append(self.open_file_item)
        self.open_file_item.connect("activate", self.open_file)

        self.share_file_item = Gtk.MenuItem(label="Share")
        self.file_menu.append(self.share_file_item)
        self.share_file_item.set_sensitive(False)
        self.share_file_item.connect("activate", self.share_file)

        self.connect_file_item = Gtk.MenuItem(label="Connect")
        self.file_menu.append(self.connect_file_item)
        self.connect_file_item.connect("activate", self.connect_file)

        self.exit_file_item = Gtk.MenuItem(label="Exit")
        self.file_menu.append(self.exit_file_item)
        self.exit_file_item.connect("activate", self.exit_app)

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

        if self.file_name is not None:
            self.textview.set_sensitive(True)
            self.share_file_item.set_sensitive(True)
            self.link = self.generate_link()
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
        if self.file_name is not None:
            self.link = self.generate_link()
            self.textview.set_sensitive(True)
            self.share_file_item.set_sensitive(True)
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
            self.textview.set_sensitive(True)
            self.link = self.entry.get_text()
            self.crdt = CRDT(self)
            self.cl = ControlLayer(self.link, self, False, self.crdt)
            self.crdt.uid = self.gen_uid()
            self.crdt.daemonise()
            self.cl.daemonize()
        else:
            pass

        self.input_dialog.destroy()

    def gen_uid(self):
        return int.from_bytes(self.cl.server.IP.encode(), "little") * self.cl.server.port

    def generate_link(self):
        """
            Generate a link to share the file
        """
        link = f"{self.IP}::{self.port}::{hashlib.sha256(self.uuid).hexdigest()}::{self.file_name}"

        return link

    def share_file(self, _):
        """
            Show link to share this file.
        """
        input_dialog = Gtk.Dialog(
            title="Share file", parent=self, modal=True
        )
        # self.input_dialog.add_buttons(
        #     Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "OK", Gtk.ResponseType.OK
        # )

        self.crdt = CRDT(self)
        # self.crdt.insert(0, self.textbuffer.get_text(self.textbuffer.get_start_iter(), self.textbuffer.get_end_iter(), True))
        self.cl = ControlLayer(self.link, self, True, self.crdt)
        self.crdt.uid = self.gen_uid()
        self.cl.daemonize()
        self.crdt.daemonise()

        # self.IP = self.cl.host_ip
        # self.port = self.cl.host_port
        # self.link = self.generate_link()

        box = input_dialog.get_content_area()
        label = Gtk.Label(label="Share this link:")

        box.add(label)
        entry = Gtk.TextView()
        entry.get_buffer().set_text(self.link)
        entry.set_editable(False)
        entry.set_wrap_mode(Gtk.WrapMode.WORD)
        box.add(entry)

        input_dialog.show_all()

        input_dialog.run()

        input_dialog.destroy()

    def exit_app(self, *args):
        """
            Exit the application
        """
        self.running = False
        if self.cl is not None:
            self.cl.stop()
        Gtk.main_quit()

    def insert_text(self, pos, text):
        """
            Insert text at the given position
        """
        self.textbuffer.insert(self.textbuffer.get_iter_at_offset(pos), text,len(text))
        if pos <= self.last_written:
            self.last_written += len(text)

    def update_text(self, text, cur_pos):
        string = text[:cur_pos] + self.textbuffer.get_text(self.textbuffer.get_iter_at_offset(self.last_written), self.textbuffer.get_iter_at_offset(self.last_written+self.counter), True) + text[cur_pos:]
        self.textbuffer.set_text(string)
        self.last_written = cur_pos
        self.textbuffer.place_cursor(self.textbuffer.get_iter_at_offset(cur_pos+self.counter))

    def rerender(self, text, cur_pos):
        """
            Rerender the text
        """
        self.update_queue.put([text, cur_pos])
        # string = text[:cur_pos] + self.textbuffer.get_text(self.textbuffer.get_iter_at_offset(self.last_written), self.textbuffer.get_iter_at_offset(self.last_written+self.counter), True) + text[cur_pos:]
        # self.textbuffer.set_text(string)
        # self.textbuffer.place_cursor(self.textbuffer.get_iter_at_offset(cur_pos+self.counter))

if __name__ == "__main__":
    win = TextEditWindow(None)
    win.connect("destroy", win.exit_app)
    win.show_all()
    try:
        Gtk.main()
    except KeyboardInterrupt:
        win.exit_app()
