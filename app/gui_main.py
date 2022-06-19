import gi

# Since a system can have multiple versions
# of GTK + installed, we want to make
# sure that we are importing GTK + 3.
gi.require_version("Gtk", "3.0")

from decryption_stack import DecryptionStack
from encryption_stack import EncryptionStack
from gi.repository import Gtk

# TODO to work towards list:
#  - provide option to encrypt file name also
#  - provide multifile tar.blah to enc/dec
#  - add logging rather than printing
#  - add tox to run app, tests and style checks and stuff like that


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Shrenc")
        self.set_border_width(10)
        Gtk.Window.set_default_size(self, 640, 480)

        # Create the outer vertical box with a space of 100 pixel.
        outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Creating stack, transition type and transition duration.
        # TODO: investigate what kind of transition types are available
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(1000)

        # add encrypt box to encrypt stack
        encryption_stack = EncryptionStack(self)
        stack.add_titled(encryption_stack.encrypt_box, "encrypt_box", "Encrypt")

        # add decrypt box to encrypt stack
        decrypt_stack = DecryptionStack(self)
        stack.add_titled(decrypt_stack.decrypt_box, "decrypt_box", "Decrypt")

        # Implementation of stack switcher.
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)

        # Put the stack switcher and the stack into the outer box
        outer_box.pack_start(stack_switcher, True, True, 0)
        outer_box.pack_start(stack, True, True, 0)

        # Add the outer box to the window
        self.add(outer_box)


def run():
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
