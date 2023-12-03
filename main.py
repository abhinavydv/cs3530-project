from gui.editor import TextEditWindow
from gi.repository import Gtk


tew = TextEditWindow(None)
tew.connect("destroy", tew.exit_app)
tew.show_all()
Gtk.main()
