from operations import decrypt_file, undo_tar_and_compress

import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

SELECTED_FILE_DEC_RESET_MSG = "File to decrypt: None chosen"


class DecryptionStack:
    def __init__(self, main_window):
        self._main_window = main_window
        self._selected_dec_filename = None
        choose_file_dec_button = Gtk.Button(label="Choose File")
        choose_file_dec_button.connect("clicked", self.on_choose_file_dec_clicked)
        self.chosen_file_dec_label = Gtk.Label(label=SELECTED_FILE_DEC_RESET_MSG)

        self._reveal_passphrase_dec = False
        self.entry_passphrase_label = Gtk.Label(label="Enter encryption passphrase")
        self.entry_passphrase_dec = Gtk.Entry()
        self.entry_passphrase_dec.set_visibility(self._reveal_passphrase_dec)
        self.entry_passphrase_dec.connect(
            "changed", self.on_dec_entry_passphrase_changed
        )
        self._dec_passphrase_entered = None
        self.entry_passphrase_toggle_dec = Gtk.CheckButton(label="Reveal passphrase?")
        self.entry_passphrase_toggle_dec.connect(
            "toggled", self.on_entry_passphrase_dec_toggled
        )
        self._decrypt_location = "./OUTPUT"
        self.choose_dec_location_button = Gtk.Button(label="Select decryption location")
        self.choose_dec_location_button.connect(
            "clicked", self.on_choose_dec_location_button_clicked
        )
        self.decrypt_location_label = Gtk.Label(
            label=f"Selected output location: {self._decrypt_location}"
        )

        self.dec_outcome_label = Gtk.Label(label="")
        self.decrypt_button = Gtk.Button(label="Decrypt")
        self.decrypt_button.connect("clicked", self.on_decrypt_clicked)
        self.decrypt_button.set_sensitive(False)

        # create the box that will home all the decryption elements, and put the buttons in
        self.decrypt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.decrypt_box.pack_start(choose_file_dec_button, True, True, 0)
        self.decrypt_box.pack_start(self.chosen_file_dec_label, True, True, 0)
        self.decrypt_box.pack_start(self.entry_passphrase_dec, True, True, 0)
        self.decrypt_box.pack_start(self.entry_passphrase_toggle_dec, True, True, 0)
        self.decrypt_box.pack_start(self.choose_dec_location_button, True, True, 0)
        self.decrypt_box.pack_start(self.decrypt_location_label, True, True, 0)
        self.decrypt_box.pack_start(
            self.decrypt_button, True, True, 0
        )  # TODO: figure out these other params
        self.decrypt_box.pack_start(self.dec_outcome_label, True, True, 0)

    def on_choose_file_dec_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file",
            parent=self._main_window,
            action=Gtk.FileChooserAction.OPEN,
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
            self.chosen_file_dec_label.set_text(
                "File to decrypt: " + self._selected_dec_filename
            )
            self.update_decryption_button_sensitivity()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def on_choose_dec_location_button_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a folder",
            parent=self._main_window,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Select clicked")
            print("Folder selected: " + dialog.get_filename())
            self._decrypt_location = dialog.get_filename()
            self.decrypt_location_label.set_text(
                f"Selected output location: {self._decrypt_location}"
            )
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def on_decrypt_clicked(self, widget):
        print("decrypt was clicked!!!!!!!")
        decryted_name = self._selected_dec_filename.rstrip(".enc")
        decrypt_file(
            self._selected_dec_filename,
            decryted_name,
            self.entry_passphrase_dec.get_text(),
        )
        print(f"finished decryption, new file exists {decryted_name}")
        undo_tar_and_compress(decryted_name, self._decrypt_location)
        print("finished uncompressing")
        os.remove(decryted_name)
        # TODO: the file that ends up in output has so many subdirs, find out why
        # TODO: all of this can probs go in some reset function thats also called on init
        self.dec_outcome_label.set_text(
            f"Success! Extracted to {self._decrypt_location}"
        )
        self.chosen_file_dec_label.set_text(SELECTED_FILE_DEC_RESET_MSG)
        self._selected_dec_filename = None
        self.update_decryption_button_sensitivity()

    def on_dec_entry_passphrase_changed(self, widget):
        self._dec_passphrase_entered = self.entry_passphrase_dec.get_text()
        self.update_decryption_button_sensitivity()

    def on_entry_passphrase_dec_toggled(self, checkbutton):
        self._reveal_passphrase_dec = self.entry_passphrase_toggle_dec.get_active()
        self.entry_passphrase_dec.set_visibility(self._reveal_passphrase_dec)

    def update_decryption_button_sensitivity(self):
        sensitivity = self._dec_passphrase_entered and self._selected_dec_filename
        self.decrypt_button.set_sensitive(sensitivity)
