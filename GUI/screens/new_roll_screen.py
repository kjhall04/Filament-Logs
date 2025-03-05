import customtkinter as ctk
import generate_barcode as gb
import spreadsheet_stats as ss

class NewRollScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.container.grid_columnconfigure((0, 1), weight=1)

        self.label = ctk.CTkLabel(self.container, text='Add New Filament')
        self.label.grid(row=0, column=0, columnspan=4, pady=(10, 20))

        # Load JSON data
        self.brand_mapping = gb.load_json('GUI\\data\\brand_mapping.json')
        self.color_mapping = gb.load_json('GUI\\data\\color_mapping.json')
        self.material_mapping = gb.load_json('GUI\\data\\material_mapping.json')
        self.attribute_mapping = gb.load_json('GUI\\data\\attribute_mapping.json')

        # Flatten nested color mapping dynamically
        self.flat_color_mapping = {}
        for category, colors in self.color_mapping.items():
            if isinstance(colors, dict):
                self.flat_color_mapping.update(colors)
            else:
                self.flat_color_mapping[category] = colors

        # Extract keys (codes) for dropdowns
        self.brands = list(self.brand_mapping.keys())
        self.colors = list(self.flat_color_mapping.keys())
        self.materials = list(self.material_mapping.keys())
        self.attributes = list(self.attribute_mapping.keys())

        self.create_dropdowns()

        self.confirm_button = ctk.CTkButton(self.container, text='Confirm Infromation', command=self.generate_barcode)
        self.confirm_button.grid(row=7, column=0, columnspan=4, pady=(20, 10))

    def create_dropdowns(self):
        dropdown_data = [
            ("Brand:", self.brands),
            ("Color:", self.colors),
            ("Material:", self.materials),
            ("Attribute 1:", self.attributes),
            ("Attribute 2:", self.attributes),
            ("Location:", ["Lab", "Storage"])
        ]

        for row, (label_text, values) in enumerate(dropdown_data, start=1):
            label = ctk.CTkLabel(self.container, text=label_text)
            label.grid(row=row, column=0, sticky="e", padx=10, pady=5)

            dropdown = ctk.CTkComboBox(self.container, values=values, state="normal")  # Typable search
            dropdown.grid(row=row, column=1, sticky="w", padx=10, pady=5)

    def generate_barcode(self):
        """Generate a barcode based on dropdown selections."""
        brand, color, material, attribute_1, attribute_2, location = [dropdown.get() for dropdown in self.dropdowns]
        sheet = ss.load_spreadsheet()

        barcode = gb.generate_filament_barcode(brand, color, material, attribute_1, attribute_2, location, sheet)

        self.confirm_button.config(text=barcode)