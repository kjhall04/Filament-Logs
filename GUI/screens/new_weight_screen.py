import customtkinter as ctk
import data_manipulation as dm
import log_data as ld

class NewWeightScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.roll_weight = None
        self.filament_weight = None

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True)

        self.step_label = ctk.CTkLabel(self.container, text="Place filament on scale and set to 'g'", font=('Arial', 18))
        self.step_label.pack(padx=20, pady=10)

        self.button = ctk.CTkButton(self.container, text='Continue', command=self.get_weight) 
        self.button.pack(padx=20, pady=10)

        self.error_label = ctk.CTkLabel(self.container, text='', text_color='red')
        self.error_label.pack(padx=10, pady=5)

    def get_weight(self):
        result = dm.get_starting_weight()

        if isinstance(result, str):
            self.error_label.configure(text=result)
            self.error_label.pack(padx=20, pady=10)
            return None, None
        
        self.roll_weight, self.filament_weight = result

        self.show_popup()

    def show_popup(self):
        """ Creates a temporary pop-up message. """
        popup = ctk.CTkToplevel(self)
        popup.title("Addition Confirmation")
        popup.geometry("300x100")  # Set popup size

        # filament_data = barcode, brand, color, material, attribute_1, attribute_2, location, sheet
        filament_data = self.master.shared_data.get('filament_data', None)
        attributes = " ".join(filter(None, [filament_data[4], filament_data[5]]))

        result = ld.log_full_filament_data(filament_data[0])

        if result:
            self.error_label.configure(text=result)

        message = f"""
            Logged
            Barcode: {filament_data[0]}
            Brand: {filament_data[1]}
            Color: {filament_data[2]}
            Material: {filament_data[3]}
            Attributes: {attributes}
            Location: {filament_data[6]}
        """

        label = ctk.CTkLabel(popup, text=message, font=("Arial", 14))
        label.pack(pady=20, padx=10)

        # Automatically close the popup after 3 seconds and switch frames
        self.after(5000, lambda: (popup.destroy(), self.master.show_frame('UserScreen')))