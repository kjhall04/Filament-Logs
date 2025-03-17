import customtkinter as ctk
import data_manipulation as dm
import spreadsheet_stats as ss

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

        self.update_weight_button = ctk.CTkButton(
            self.container,
            text='Update Weight',
            command=lambda: self.master.show_frame('UpdateCurrentWeightScreen')
        )

        # Bind the event to check when the content of the entry is modified
        self.barcode_entry.bind("<KeyRelease>", self.check_barcode_length)

    def check_barcode_length(self, event):
        barcode = self.barcode_entry.get()
        
        valid_barcode = dm.validate_barcode(barcode)

        if valid_barcode == barcode:
            self.process_barcode(barcode)
            self.barcode_entry.pack_forget() 
        else:
            self.ready_label.configure(text='Barcode Invalid. Please scan again.')

    def process_barcode(self, barcode):
        self.ready_label.configure(text=f"Scanned Barcode: {barcode}")

        filament_data = dm.decode_barcode(barcode)
        sheet = ss.load_spreadsheet()
        print(barcode)
        print(sheet)
        current_filament_weight = self.get_current_filament_weight(barcode, sheet)

        self.filament_data.configure(text='\n'.join(filter(None, [
            filament_data[0],
            filament_data[1],
            filament_data[2],
            current_filament_weight + ' g',
            filament_data[3] if filament_data[3] else None,
            filament_data[4] if filament_data[4] else None,
            filament_data[5],
        ])))
        
        self.filament_data.pack(padx=20, pady=10)
        self.update_weight_button.pack(padx=20, pady=10)

    def get_current_filament_weight(self, barcode, sheet) -> float:
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[1] == barcode:
                return row[-4]