import os
import time
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from operations import encrypt_file, tar_and_compress


SELECTED_FILE_ENC_RESET_MSG = "File to encrypt: None chosen"


class EncryptionStack:
    def __init__(self, main_window):
        self.main_window = main_window
        self._selected_enc_filename = None
        # make choose file and encrypt buttons
        choose_file_enc_button = Gtk.Button(label="Choose File")
        choose_file_enc_button.connect("clicked", self.on_choose_file_enc_clicked)
        self.chosen_file_enc_label = Gtk.Label(label=SELECTED_FILE_ENC_RESET_MSG)
        self.enc_outcome_label = Gtk.Label(label="")
        self.encrypt_button = Gtk.Button(label="Encrypt")
        self.encrypt_button.connect("clicked", self.on_encrypt_clicked)
        self.armor_toggle = Gtk.CheckButton(label="Use armor?")

        # TODO: should not be able to hit encrypt without a passphrase
        self._reveal_passphrase_enc = False
        self.entry_passphrase_label = Gtk.Label(label="Enter encryption passphrase")
        self.entry_passphrase = Gtk.Entry()
        self._enc_passphrase_entered = None
        self.entry_passphrase.set_visibility(self._reveal_passphrase_enc)
        self.entry_passphrase.connect("changed", self.on_enc_entry_passphrase_changed)
        self.entry_passphrase_toggle = Gtk.CheckButton(label="Reveal passphrase?")
        self.entry_passphrase_toggle.connect(
            "toggled", self.on_entry_passphrase_toggled
        )

        # need this so the labels in the various list stores actually get applied to the comboboxes
        renderer_text = Gtk.CellRendererText()

        self._selected_compression_label = Gtk.Label(label="Select compression")
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
        self.compression_combo = Gtk.ComboBox.new_with_model(compression_store)
        self.compression_combo.connect("changed", self.on_compression_combo_changed)
        self.compression_combo.set_entry_text_column(0)

        self.compression_combo.pack_start(renderer_text, True)
        self.compression_combo.add_attribute(renderer_text, "text", 0)
        self.compression_combo.set_active(0)  # set zgip as the default

        self._select_cypher_label = Gtk.Label(label="Select cypher algorithm")
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
        self.cypher_combo = Gtk.ComboBox.new_with_model(cypher_store)
        self.cypher_combo.connect("changed", self.on_cypher_combo_changed)

        self.cypher_combo.pack_start(renderer_text, True)
        self.cypher_combo.add_attribute(renderer_text, "text", 0)
        self.cypher_combo.set_active(6)  # set AES256 as the default
        self.encrypt_button.set_sensitive(False)

        # create the box that will home all the encryption elements, and put the buttons in
        self.encrypt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.encrypt_box.pack_start(choose_file_enc_button, True, True, 0)
        # TODO: this choose file needs to be a "choose file OR folder"
        self.encrypt_box.pack_start(self.chosen_file_enc_label, True, True, 0)
        self.encrypt_box.pack_start(self.entry_passphrase_label, True, True, 0)
        self.encrypt_box.pack_start(self.entry_passphrase, True, True, 0)
        self.encrypt_box.pack_start(self.entry_passphrase_toggle, True, True, 0)
        self.encrypt_box.pack_start(self._selected_compression_label, True, True, 0)
        self.encrypt_box.pack_start(self.compression_combo, True, True, 0)
        self.encrypt_box.pack_start(self.armor_toggle, True, True, 0)
        self.encrypt_box.pack_start(self._select_cypher_label, True, True, 0)
        self.encrypt_box.pack_start(self.cypher_combo, True, True, 0)
        self.encrypt_box.pack_start(
            self.encrypt_button, True, True, 0
        )  # TODO: figure out these other params
        self.encrypt_box.pack_start(self.enc_outcome_label, True, True, 0)

    def on_cypher_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            self._selected_cypher = model[tree_iter][0]
            print("Selected: cypher=%s" % self._selected_cypher)

    def on_compression_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            self._selected_compression = model[tree_iter][1]
            print("selected compression:", self._selected_compression)

    def on_choose_file_enc_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file",
            parent=self.main_window,
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
            self._selected_enc_filename = dialog.get_filename()
            self.chosen_file_enc_label.set_text(
                "File to encrypt: " + self._selected_enc_filename
            )
            self.update_encryption_button_sensitivity()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def on_encrypt_clicked(self, widget):
        print("encrypt was clicked!!!!!!!")
        # TODO: add mechanism to provide a name for the compressed archive
        name = time.time()
        name = str(name).replace(".", "_")
        compressed_name = tar_and_compress(
            self._selected_enc_filename, name, self._selected_compression
        )
        print(f"finished compressing file {compressed_name}")
        encrypted_name = compressed_name + ".enc"
        encrypt_file(
            compressed_name,
            encrypted_name,
            self._enc_passphrase_entered,
            symmetric=self._selected_cypher,
            armor=self.armor_toggle.get_active(),
        )
        print(
            "finished encrypting with "
            f"passphrase={self._enc_passphrase_entered} "
            f"cypher={self._selected_cypher} "
            f"armor={self.armor_toggle.get_active()}"
        )
        print(f"new file exists {encrypted_name}")
        print(f"removing intermediate file {compressed_name}")
        os.remove(compressed_name)
        # TODO: all of this can probs go in some reset function thats also called on init
        self.enc_outcome_label.set_text("Success!: Created " + encrypted_name)
        self.chosen_file_enc_label.set_text(SELECTED_FILE_ENC_RESET_MSG)
        self._selected_enc_filename = None
        self.encrypt_button.set_sensitive(False)

    def on_enc_entry_passphrase_changed(self, widget):
        self._enc_passphrase_entered = self.entry_passphrase.get_text()
        self.update_encryption_button_sensitivity()

    def on_entry_passphrase_toggled(self, checkbutton):
        # is it necessary to have the self._reveal_passphrase_enc attr?
        self._reveal_passphrase_enc = self.entry_passphrase_toggle.get_active()
        self.entry_passphrase.set_visibility(self._reveal_passphrase_enc)

    def update_encryption_button_sensitivity(self):
        print("self._enc_passphrase_entered:", self._enc_passphrase_entered)
        print("self._selected_enc_filename:", self._selected_enc_filename)

        sensitivity = self._enc_passphrase_entered and self._selected_enc_filename
        self.encrypt_button.set_sensitive(sensitivity)
