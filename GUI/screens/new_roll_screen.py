import customtkinter as ctk
import generate_barcode as gb
import spreadsheet_stats as ss

class NewRollScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew", padx=320, pady=60)

        self.container.grid_columnconfigure((0, 1), weight=1)

        self.label = ctk.CTkLabel(self.container, text='Add New Filament', font=('Arial', 20))
        self.label.grid(row=0, column=0, columnspan=4, pady=10)

        self.create_entry_boxes()

        self.confirm_button = ctk.CTkButton(self.container, text='Confirm Infromation', command=self.confirm_and_clear)
        self.confirm_button.grid(row=7, column=0, columnspan=4, pady=(20, 10))

        self.error_label = ctk.CTkLabel(self.container, text='', text_color='red')

    def create_entry_boxes(self):
        label_data = ['Brand:', 'Color:', 'Material:', 'Attribute 1:', 'Attribute 2:', 'Location:']

        self.entries = []

        for row, label_text in enumerate(label_data, start=1):
            label = ctk.CTkLabel(self.container, text=label_text)
            label.grid(row=row, column=0, sticky="e", padx=10, pady=5)

            entry = ctk.CTkEntry(self.container, width=160)  # Typable search
            entry.grid(row=row, column=1, sticky="w", padx=10, pady=5)

            self.entries.append(entry)

    def generate_barcode(self):
        """Generate a barcode based on typed entries."""
        brand, color, material, attribute_1, attribute_2, location = [entry.get() for entry in self.entries]
        sheet = ss.load_spreadsheet()

        barcode = gb.generate_filament_barcode(brand, color, material, attribute_1, attribute_2, location, sheet)

        data = barcode, brand, color, material, attribute_1, attribute_2, location, sheet

        if barcode.startswith('Invalid'):
            self.error_label.configure(text=barcode)
            self.error_label.grid(row=8, column=0, columnspan=4, pady=(20, 10))
            self.error_label.update_idletasks()
        else:
            self.error_label.configure(text='')
            self.error_label.grid_remove()

            self.master.shared_data['filament_data'] = data

            self.master.show_frame('NewWeightScreen')   

    def clear_entries(self):
        for entry in self.entries:
            entry.delete(0, 'end')

    def confirm_and_clear(self):
        self.generate_barcode()  # Run first
        if not self.error_label.winfo_ismapped():  # Clear only if there’s no error
            self.clear_entries()
