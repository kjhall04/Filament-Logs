import customtkinter as ctk
import backend.data_manipulation as dm
import time

class UserScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True)

        self.ready_label = ctk.CTkLabel(self.container, text='Ready to scan barcode...', font=('Arial', 16))
        self.ready_label.pack(padx=20, pady=20)

        self.barcode_entry = ctk.CTkEntry(self.container)
        self.barcode_entry.pack(padx=20, pady=10)

        self.filament_data = ctk.CTkLabel(self.container)

        # Bind the event to check when the content of the entry is modified
        self.barcode_entry.bind("<KeyRelease>", self.check_barcode_length)

    def check_barcode_length(self, event):
        """Check if the barcode entry has reached a certain length."""
        barcode = self.barcode_entry.get()
        
        valid_barcode = dm.validate_barcode(self.barcode_entry)

        if valid_barcode == barcode:
            self.process_barcode(barcode)
            self.barcode_entry.pack_forget() 
        else:
            self.ready_label.configure(text='Barcode Invalid. Please scan again.')

    def process_barcode(self, barcode):
        """Process the scanned barcode."""
        self.ready_label.configure(text=f"Scanned Barcode: {barcode}")

        filament_data = dm.decode_barcode(barcode)

        self.filament_data.configure(text=f'{filament_data[0]}')
        self.filament_data.pack(padx=20, pady=10)
        