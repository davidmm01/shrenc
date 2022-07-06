import datetime
import logging
import os
import random
import string
import time

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from operations import encrypt_file, PARAM_TO_TAR_COMPRESS_SETTINGS, tar_and_compress

logger = logging.getLogger(__name__)


# initial/default labels and prompts
SELECTED_FILE_RESET_MSG = "File to encrypt: None chosen"
CHOOSE_FILE_BUTTON_TEXT = "Choose File"
ENCRYPT_BUTTON_TEXT = "Encrypt"
OUTCOME_INIT_TEXT = ""
ARMOR_TOGGLE_TEXT = "Use armor?"
PASSPHRASE_TOGGLE_VISIBILITY_TEXT = "Reveal passphrase?"
COMPRESSION_SELECTION_PROMPT = "Select compression"
ENTER_PASSPHRASE_PROMPT = "Enter encryption passphrase"
CYPHER_SELECTION_PROMPT = "Select cypher algorithm"
FILE_PICKER_PROMPT = "Please choose a file"
OUTPUT_NAMING_PROMPT = "Choose name of encrypted file"

ENCRYPTED_EXTENSION = ".enc"

RANDOM_PASSWORD_LENGTH = 12


class EncryptionStack:
    def __init__(self, main_window):
        self._main_window = main_window

        # File selection
        self._selected_filename = None
        choose_file_button = Gtk.Button(label=CHOOSE_FILE_BUTTON_TEXT)
        choose_file_button.connect("clicked", self._on_choose_file_clicked)
        self._chosen_file_label = Gtk.Label(label=SELECTED_FILE_RESET_MSG)

        # Outcome feedback
        self._outcome_label = Gtk.Label(label=OUTCOME_INIT_TEXT)

        # Encryption button
        self._encrypt_button = Gtk.Button(label=ENCRYPT_BUTTON_TEXT)
        self._encrypt_button.connect("clicked", self._on_encrypt_clicked)
        self._encrypt_button.set_sensitive(False)

        # Amor toggle
        self._armor_toggle = Gtk.CheckButton(label=ARMOR_TOGGLE_TEXT)

        # Passphrase entry and associated controls
        entry_passphrase_label = Gtk.Label(label=ENTER_PASSPHRASE_PROMPT)
        self._entry_passphrase_toggle = Gtk.CheckButton(
            label=PASSPHRASE_TOGGLE_VISIBILITY_TEXT
        )
        self._entry_passphrase_toggle.connect(
            "toggled", self._on_entry_passphrase_toggled
        )
        self._entry_passphrase = Gtk.Entry()
        self._enc_passphrase_entered = None
        self._entry_passphrase.set_visibility(
            self._entry_passphrase_toggle.get_active()
        )
        self._entry_passphrase.connect("changed", self._on_entry_passphrase_changed)

        # Output naming controls
        output_naming_label = Gtk.Label(label=OUTPUT_NAMING_PROMPT)
        output_naming_radio_box = Gtk.Box(spacing=6)
        radio_button_1 = Gtk.RadioButton.new_with_label_from_widget(
            None, "Epoch timestamp"
        )
        radio_button_1.connect("toggled", self._on_radio_button_toggled, "epoch")
        radio_button_2 = Gtk.RadioButton.new_with_label_from_widget(
            radio_button_1, "ISO timestamp"
        )
        radio_button_2.connect("toggled", self._on_radio_button_toggled, "iso")
        radio_button_3 = Gtk.RadioButton.new_with_label_from_widget(
            radio_button_2, "Garbage"
        )
        radio_button_3.connect("toggled", self._on_radio_button_toggled, "random")
        radio_button_4 = Gtk.RadioButton.new_with_label_from_widget(
            radio_button_3, "Custom"
        )
        radio_button_4.connect("toggled", self._on_radio_button_toggled, "custom")

        output_naming_radio_box.pack_start(radio_button_1, False, False, 0)
        output_naming_radio_box.pack_start(radio_button_2, False, False, 0)
        output_naming_radio_box.pack_start(radio_button_3, False, False, 0)
        output_naming_radio_box.pack_start(radio_button_4, False, False, 0)
        self._output_naming_entry = Gtk.Entry()
        self._output_naming_entry.set_sensitive(False)
        self._set_epoch_on_output_naming_entry()

        # Compression selection
        selected_compression_label = Gtk.Label(label=COMPRESSION_SELECTION_PROMPT)
        self._selected_compression = "gzip"
        compression_store = Gtk.ListStore(str, str)
        compression_options = [
            ["gzip (.tar.gz)", "gzip"],
            ["bz2 (.tar.bz2)", "bz2"],
            ["lzma (.tar.xz)", "lzma"],
            ["No compression (.tar)", "tar_only"],
        ]
        for compression_option in compression_options:
            compression_store.append(compression_option)
        compression_combo = Gtk.ComboBox.new_with_model(compression_store)
        compression_combo.connect("changed", self._on_compression_combo_changed)
        compression_combo.set_entry_text_column(0)
        # need this so the labels in the various list stores actually get applied to the comboboxes
        renderer_text = Gtk.CellRendererText()
        compression_combo.pack_start(renderer_text, True)
        compression_combo.add_attribute(renderer_text, "text", 0)
        compression_combo.set_active(0)  # set zgip as the default

        # Cypher selection
        select_cypher_label = Gtk.Label(label=CYPHER_SELECTION_PROMPT)
        self._selected_cypher = "AES256"
        cypher_store = Gtk.ListStore(str)
        # TODO: could the available cyphers be worked out from the version
        # info of GPG? Would protect from using one that is invalid with the version of GPG.
        # Atleast make the cyphers a constant later if no logic
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
        cypher_combo = Gtk.ComboBox.new_with_model(cypher_store)
        cypher_combo.connect("changed", self._on_cypher_combo_changed)
        cypher_combo.pack_start(renderer_text, True)
        cypher_combo.add_attribute(renderer_text, "text", 0)
        cypher_combo.set_active(6)  # set AES256 as the default

        # Create the box that will home all the encryption elements, and put
        # everything inside
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.box.pack_start(choose_file_button, True, True, 0)
        # TODO: this choose file needs to be a "choose file OR folder"
        self.box.pack_start(self._chosen_file_label, True, True, 0)
        self.box.pack_start(entry_passphrase_label, True, True, 0)
        self.box.pack_start(self._entry_passphrase, True, True, 0)
        self.box.pack_start(self._entry_passphrase_toggle, True, True, 0)
        self.box.pack_start(selected_compression_label, True, True, 0)
        self.box.pack_start(compression_combo, True, True, 0)
        self.box.pack_start(self._armor_toggle, True, True, 0)
        self.box.pack_start(select_cypher_label, True, True, 0)
        self.box.pack_start(cypher_combo, True, True, 0)
        self.box.pack_start(output_naming_label, True, True, 0)
        self.box.pack_start(output_naming_radio_box, True, True, 0)
        self.box.pack_start(self._output_naming_entry, True, True, 0)
        self.box.pack_start(
            self._encrypt_button, True, True, 0
        )  # TODO: figure out these other params
        self.box.pack_start(self._outcome_label, True, True, 0)

    def _on_cypher_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            self._selected_cypher = model[tree_iter][0]
            logger.debug(f"self._selected_cypher={self._selected_cypher}")

    def _on_compression_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            self._selected_compression = model[tree_iter][1]
            logger.debug(f"self._selected_compression={self._selected_compression}")
            self._apply_ext_to_output_naming_entry()

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
            logger.debug(f"self._selected_filename={self._selected_filename}")
            self._chosen_file_label.set_text(
                "File to encrypt: " + self._selected_filename
            )
            self._update_encryption_button_sensitivity()

        dialog.destroy()

    def _on_encrypt_clicked(self, widget):
        comp_ext = PARAM_TO_TAR_COMPRESS_SETTINGS[self._selected_compression]["ext"]
        full_ext = f"{comp_ext}{ENCRYPTED_EXTENSION}"

        # if the name looks OK, proceed to encrpyt without any warnings
        if self._output_naming_entry.get_text().endswith(full_ext):
            self._do_encryption()
            return

        # else if the entered name does not look correct, warn the user first
        # before proceeding
        dialog = Gtk.Dialog(
            title="Warning!",
            parent=self._main_window,
        )
        detail = (
            f"The selected file name '{self._output_naming_entry.get_text()}' does "
            "not have the right extension for the selected compression\nIt should "
            f"end in {full_ext}\nShrenc may not know how to decrpyt this file in the "
            "future.\nAre you sure you want to continue?"
        )
        label = Gtk.Label(label=detail)
        box = dialog.get_content_area()
        box.add(label)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK,
            Gtk.ResponseType.OK,
        )
        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self._do_encryption()

        dialog.destroy()

    def _do_encryption(self):
        temp_filename = time.time()
        temp_filename = str(temp_filename).replace(".", "_")
        compressed_name = tar_and_compress(
            self._selected_filename, temp_filename, self._selected_compression
        )
        logger.debug(f"finished compressing file {compressed_name}")
        encrypt_file(
            compressed_name,
            self._output_naming_entry.get_text(),
            self._enc_passphrase_entered,
            symmetric=self._selected_cypher,
            armor=self._armor_toggle.get_active(),
        )
        logger.info(
            "finished encrypting with "
            f"passphrase={self._enc_passphrase_entered} "
            f"cypher={self._selected_cypher} "
            f"armor={self._armor_toggle.get_active()} "
            f"file_created={self._output_naming_entry.get_text()} "
        )
        logger.debug(f"removing intermediate file {compressed_name}")
        os.remove(compressed_name)
        # TODO: all of this can probs go in some reset function thats also called on init
        self._outcome_label.set_text(
            "Success!: Created " + self._output_naming_entry.get_text()
        )
        self._chosen_file_label.set_text(SELECTED_FILE_RESET_MSG)
        self._selected_filename = None
        self._encrypt_button.set_sensitive(False)

    def _on_entry_passphrase_changed(self, widget):
        # TODO: add passphrase strength feedback
        self._enc_passphrase_entered = self._entry_passphrase.get_text()
        self._update_encryption_button_sensitivity()

    def _on_entry_passphrase_toggled(self, checkbutton):
        self._entry_passphrase.set_visibility(
            self._entry_passphrase_toggle.get_active()
        )

    def _update_encryption_button_sensitivity(self):
        sensitivity = self._enc_passphrase_entered and self._selected_filename
        self._encrypt_button.set_sensitive(sensitivity)

    def _on_radio_button_toggled(self, button, name):
        if name == "epoch" and button.get_active():
            self._output_naming_entry.set_sensitive(False)
            self._set_epoch_on_output_naming_entry()

        elif name == "iso" and button.get_active():
            self._output_naming_entry.set_sensitive(False)

            self._output_naming_entry.set_text(
                datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")
            )

        elif name == "random" and button.get_active():
            self._output_naming_entry.set_sensitive(False)
            source = string.ascii_lowercase + string.digits
            result_str = "".join(
                random.choice(source) for i in range(RANDOM_PASSWORD_LENGTH)
            )
            self._output_naming_entry.set_text(result_str)

        elif name == "custom" and button.get_active():
            self._output_naming_entry.set_sensitive(True)

        self._apply_ext_to_output_naming_entry()

    def _apply_ext_to_output_naming_entry(self):
        text = self._output_naming_entry.get_text()
        extensions = [
            PARAM_TO_TAR_COMPRESS_SETTINGS[key]["ext"]
            for key in PARAM_TO_TAR_COMPRESS_SETTINGS
        ]
        for ext in extensions:
            full_ext = ext + ENCRYPTED_EXTENSION
            if text.endswith(full_ext):
                text = text.rstrip(full_ext)
                break
        text = (
            text
            + PARAM_TO_TAR_COMPRESS_SETTINGS[self._selected_compression]["ext"]
            + ENCRYPTED_EXTENSION
        )
        self._output_naming_entry.set_text(text)

    def _set_epoch_on_output_naming_entry(self):
        self._output_naming_entry.set_text(str(time.time()).replace(".", "_"))
