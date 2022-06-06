import gi
# Since a system can have multiple versions
# of GTK + installed, we want to make
# sure that we are importing GTK + 3.
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from operations import compress_file, encrypt_file, decrypt_file, uncompress_file


# to work towards list:
#  - provide name for decrypt output
#  - provide option to encrypt file name also
#  - provide multifile tar.gz to enc/dec
#  - add logging rather than printing
#  - provide option to supply enc/dec passphrase


SELECTED_FILE_ENC_RESET_MSG = "File to encrypt: None chosen"
SELECTED_FILE_DEC_RESET_MSG = "File to decrypt: None chosen"

class MainWindow(Gtk.Window):
    # TODO: oh god this init is very gross, address before its too late...
    # maybe start with an encryption stack class?
    def __init__(self):
        Gtk.Window.__init__(self, title ="Shrenc")
        self.set_border_width(10)
        Gtk.Window.set_default_size(self, 640, 480)

        self._selected_enc_filename = SELECTED_FILE_ENC_RESET_MSG
        self._selected_dec_filename = SELECTED_FILE_DEC_RESET_MSG

        # Create the outer vertical box with a space of 100 pixel.
        outer_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 100)

        # Creating stack, transition type and transition duration.
        # TODO: investigate what kind of transition types are available
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(1000)

        # make choose file and encrypt buttons
        choose_file_enc_button = Gtk.Button(label="Choose File")
        choose_file_enc_button.connect("clicked", self.on_choose_file_enc_clicked)
        self.chosen_file_enc_label = Gtk.Label(label=self._selected_enc_filename)
        self.enc_outcome_label = Gtk.Label(label="")
        self.encrypt_button = Gtk.Button(label="Encrypt")
        self.encrypt_button.connect("clicked", self.on_encrypt_clicked)
        self.armor_toggle = Gtk.CheckButton(label="Use armor?")
        self._selected_cypher = "IDEA"
        cypher_store = Gtk.ListStore(str)
        # TODO: could the available cyphers be worked out from the version
        # info of GPG? Would protect from using one that is invalid with the version of GPG.
        cyphers = [
            "IDEA",
            "3DES",
            "CAST5",
            "BLOWFISH",
            "AES",
            "AES192",
            "AES256",
            "TWOFISH",
            "CAMELLIA128",
            "CAMELLIA192",
            "CAMELLIA256",
        ]
        for cypher in cyphers:
            cypher_store.append([cypher])
        self.cypher_combo = Gtk.ComboBox.new_with_model(cypher_store)
        self.cypher_combo.connect("changed", self.on_cypher_combo_changed)
        # need this so the labels in the list store actually get applied to the combobox
        renderer_text = Gtk.CellRendererText()
        self.cypher_combo.pack_start(renderer_text, True)
        self.cypher_combo.add_attribute(renderer_text, "text", 0)
        self.cypher_combo.set_active(6)  # set AES256 as the default
        self.encrypt_button.set_sensitive(False)

        # create the box that will home all the encryption elements, and put the buttons in
        encrypt_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 100)
        encrypt_box.pack_start(choose_file_enc_button, True, True, 0)
        encrypt_box.pack_start(self.chosen_file_enc_label, True, True, 0)
        encrypt_box.pack_start(self.armor_toggle, True, True, 0)
        encrypt_box.pack_start(self.cypher_combo, True, True, 0)
        encrypt_box.pack_start(self.encrypt_button, True, True, 0)  # TODO: figure out these other params
        encrypt_box.pack_start(self.enc_outcome_label, True, True, 0)

        # add encrypt box to encrypt stack
        stack.add_titled(encrypt_box, "encrypt_box", "Encrypt")

        # Decrypt
        choose_file_dec_button = Gtk.Button(label="Choose File")
        choose_file_dec_button.connect("clicked", self.on_choose_file_dec_clicked)
        self.chosen_file_dec_label = Gtk.Label(label=self._selected_dec_filename)
        self.dec_outcome_label = Gtk.Label(label="")
        self.decrypt_button = Gtk.Button(label="Decrypt")
        self.decrypt_button.connect("clicked", self.on_decrypt_clicked)
        self.decrypt_button.set_sensitive(False)

        # create the box that will home all the decryption elements, and put the buttons in
        decrypt_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 100)
        decrypt_box.pack_start(choose_file_dec_button, True, True, 0)
        decrypt_box.pack_start(self.chosen_file_dec_label, True, True, 0)
        decrypt_box.pack_start(self.decrypt_button, True, True, 0)  # TODO: figure out these other params
        decrypt_box.pack_start(self.dec_outcome_label, True, True, 0)

        # add decrypt box to encrypt stack
        stack.add_titled(decrypt_box, "decrypt_box", "Decrypt")

        # Implementation of stack switcher.
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)

        # Put the stack switcher and the stack into the outer box
        outer_box.pack_start(stack_switcher, True, True, 0)
        outer_box.pack_start(stack, True, True, 0)

        # Add the outer box to the window
        self.add(outer_box)

    def on_cypher_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            self._selected_cypher = model[tree_iter][0]
            print("Selected: cypher=%s" % self._selected_cypher)

    # TODO: refactor following two methods DRY
    def on_choose_file_enc_clicked(self, widget):
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
            self._selected_enc_filename = dialog.get_filename()
            self.chosen_file_enc_label.set_text("File to encrypt: " + self._selected_enc_filename)
            self.encrypt_button.set_sensitive(True)
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def on_choose_file_dec_clicked(self, widget):
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
            self._selected_dec_filename = dialog.get_filename()
            self.chosen_file_dec_label.set_text("File to decrypt: " + self._selected_dec_filename)
            self.decrypt_button.set_sensitive(True)
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def on_encrypt_clicked(self, widget):
        print("encrypt was clicked!!!!!!!")
        compressed_name = self._selected_enc_filename + ".gz"
        encrypted_name = compressed_name + ".enc"
        compress_file(self._selected_enc_filename, compressed_name)
        print("finished compressing")
        encrypt_file(
            compressed_name,
            encrypted_name,
            symmetric=self._selected_cypher,
            armor=self.armor_toggle.get_active()
        )
        print(
            "finished encrypting with "
            f"cypher={self._selected_cypher} "
            f"armor={self.armor_toggle.get_active()}"
        )
        # TODO: all of this can probs go in some reset function thats also called on init
        self.enc_outcome_label.set_text("Success!: Created " + encrypted_name)
        self.chosen_file_enc_label.set_text(SELECTED_FILE_ENC_RESET_MSG)
        self._selected_enc_filename = None
        self.encrypt_button.set_sensitive(False)

    def on_decrypt_clicked(self, widget):
        print("decrypt was clicked!!!!!!!")
        decryted_name = self._selected_dec_filename + ".dec"
        uncompressed_name = decryted_name + ".unc"
        decrypt_file(self._selected_dec_filename, decryted_name)
        print("finished decryption")
        uncompress_file(decryted_name, uncompressed_name)
        print("finished uncompressing")
        # TODO: all of this can probs go in some reset function thats also called on init
        self.dec_outcome_label.set_text("Success!: Created " + uncompressed_name)
        self.chosen_file_dec_label.set_text(SELECTED_FILE_DEC_RESET_MSG)
        self._selected_dec_filename = None
        self.decrypt_button.set_sensitive(False)

win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
