import logging
import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from operations import decrypt_file, undo_tar_and_compress

logger = logging.getLogger(__name__)


# initial/default labels and prompts
SELECTED_FILE_RESET_MSG = "File to decrypt: None chosen"
CHOOSE_FILE_BUTTON_TEXT = "Choose File"
ENTER_PASSPHRASE_PROMPT = "Enter decryption passphrase"
PASSPHRASE_TOGGLE_VISIBILITY_TEXT = "Reveal passphrase?"
SELECT_DECRYPTION_LOCATION_PROMPT = "Select decryption location"
DECRYPT_BUTTON_TEXT = "Decrypt"
FILE_PICKER_PROMPT = "Please choose a file"
LOCATION_PICKER_PROMPT = "Please choose a folder"


class DecryptionStack:
    def __init__(self, main_window):
        self._main_window = main_window

        # File selection
        self._selected_filename = None
        choose_file_button = Gtk.Button(label=CHOOSE_FILE_BUTTON_TEXT)
        choose_file_button.connect("clicked", self._on_choose_file_clicked)
        self._chosen_file_label = Gtk.Label(label=SELECTED_FILE_RESET_MSG)

        # Outcome feedback
        self._outcome_label = Gtk.Label(label="")

        # Passphrase entry and associated controls
        self._entry_passphrase_label = Gtk.Label(label=ENTER_PASSPHRASE_PROMPT)
        self._entry_passphrase = Gtk.Entry()
        self._entry_passphrase.set_visibility(False)
        self._entry_passphrase.connect("changed", self._on_entry_passphrase_changed)
        self._passphrase_entered = None
        self._entry_passphrase_toggle = Gtk.CheckButton(
            label=PASSPHRASE_TOGGLE_VISIBILITY_TEXT
        )
        self._entry_passphrase_toggle.connect(
            "toggled", self._on_entry_passphrase_toggled
        )

        # Decryption output controls
        self._decrypt_location = "./OUTPUT"
        self.choose_dec_location_button = Gtk.Button(
            label=SELECT_DECRYPTION_LOCATION_PROMPT
        )
        self.choose_dec_location_button.connect(
            "clicked", self._on_choose_dec_location_button_clicked
        )
        self.decrypt_location_label = Gtk.Label(
            label=f"Selected output location: {self._decrypt_location}"
        )

        # Decrypt button
        self.decrypt_button = Gtk.Button(label=DECRYPT_BUTTON_TEXT)
        self.decrypt_button.connect("clicked", self._on_decrypt_clicked)
        self.decrypt_button.set_sensitive(False)

        # Create the box that will home all the decryption elements, and put
        # everything inside
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.box.pack_start(choose_file_button, True, True, 0)
        self.box.pack_start(self._chosen_file_label, True, True, 0)
        self.box.pack_start(self._entry_passphrase, True, True, 0)
        self.box.pack_start(self._entry_passphrase_toggle, True, True, 0)
        self.box.pack_start(self.choose_dec_location_button, True, True, 0)
        self.box.pack_start(self.decrypt_location_label, True, True, 0)
        self.box.pack_start(self.decrypt_button, True, True, 0)
        self.box.pack_start(self._outcome_label, True, True, 0)

    def _on_choose_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title=FILE_PICKER_PROMPT,
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
            self._selected_filename = dialog.get_filename()
            self._chosen_file_label.set_text(
                "File to decrypt: " + self._selected_filename
            )
            logger.debug(f"self._selected_filename={self._selected_filename}")
            self._update_decryption_button_sensitivity()

        dialog.destroy()

    def _on_choose_dec_location_button_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title=LOCATION_PICKER_PROMPT,
            parent=self._main_window,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self._decrypt_location = dialog.get_filename()
            logger.debug(f"self._decrypt_location={self._decrypt_location}")
            self.decrypt_location_label.set_text(
                f"Selected output location: {self._decrypt_location}"
            )

        dialog.destroy()

    def _on_decrypt_clicked(self, widget):
        decryted_name = self._selected_filename.rstrip(".enc")
        decrypt_file(
            self._selected_filename,
            decryted_name,
            self._entry_passphrase.get_text(),
        )
        logger.debug(f"finished decryption, new file exists {decryted_name}")
        undo_tar_and_compress(decryted_name, self._decrypt_location)
        logger.info("finished uncompressing")
        os.remove(decryted_name)
        # TODO: the file that ends up in output has so many subdirs, find out why
        # TODO: all of this can probs go in some reset function thats also called on init
        self._outcome_label.set_text(f"Success! Extracted to {self._decrypt_location}")
        self._chosen_file_label.set_text(SELECTED_FILE_RESET_MSG)
        self._selected_filename = None
        self._update_decryption_button_sensitivity()

    def _on_entry_passphrase_changed(self, widget):
        self._passphrase_entered = self._entry_passphrase.get_text()
        self._update_decryption_button_sensitivity()

    def _on_entry_passphrase_toggled(self, checkbutton):
        self._entry_passphrase.set_visibility(
            self._entry_passphrase_toggle.get_active()
        )

    def _update_decryption_button_sensitivity(self):
        sensitivity = self._passphrase_entered and self._selected_filename
        self.decrypt_button.set_sensitive(sensitivity)
