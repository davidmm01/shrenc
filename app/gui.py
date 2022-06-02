import gi
# Since a system can have multiple versions
# of GTK + installed, we want to make
# sure that we are importing GTK + 3.
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from operations import compress_file, encrypt_file

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title ="Shrenc")
        self.set_border_width(10)
        Gtk.Window.set_default_size(self, 640, 480)

        self._selected_filename = "File to encrypt: None chosen"

        # Create the outer vertical box with a space of 100 pixel.
        outer_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 100)

        # Creating stack, transition type and transition duration.
        # TODO: investigate what kind of transition types are available
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(1000)

        # make choose file and encrypt buttons
        choose_file_button = Gtk.Button(label="Choose File")
        choose_file_button.connect("clicked", self.on_choose_file_clicked)
        self.chosen_file_label = Gtk.Label(label=self._selected_filename)
        encrypt_button = Gtk.Button(label="Encrypt")
        encrypt_button.connect("clicked", self.on_encrypt_clicked)

        # create the box that will home all the encryption elements, and put the buttons in
        encrypt_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 100)
        encrypt_box.pack_start(choose_file_button, True, True, 0)
        encrypt_box.pack_start(self.chosen_file_label, True, True, 0)
        encrypt_box.pack_start(encrypt_button, True, True, 0)  # TODO: figure out these other params

        # add encrypt b to encrypt stack
        stack.add_titled(encrypt_box, "box", "Encrypt")

        # add choose file button to encrypt stack
        stack.add_titled(choose_file_button, "button", "Encrypt")

        # Decrypt
        label = Gtk.Label()
        label.set_markup("<big>TODO!</big>")
        stack.add_titled(label, "label", "Decrypt")

        # Implementation of stack switcher.
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)

        # Put the stack switcher and the stack into the outer box
        outer_box.pack_start(stack_switcher, True, True, 0)
        outer_box.pack_start(stack, True, True, 0)

        # Add the outer box to the window
        self.add(outer_box)

    def on_choose_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            self._selected_filename = dialog.get_filename()
            self.chosen_file_label.set_text("File to encrypt: " + self._selected_filename)
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def on_encrypt_clicked(self, widget):
        print("encrypt was clicked!!!!!!!")
        compressed_name = self._selected_filename + ".gz"
        encrypted_name = compressed_name + ".enc"
        compress_file(self._selected_filename, compressed_name)
        print("finished compressing")
        encrypt_file(compressed_name, encrypted_name)
        print("finished encrypting")


win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
