import customtkinter as ctk
import data_manipulation as dm
import log_data as ld

class UpdateCurrentWeightScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.filament_amount = None

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True)

        self.step_label = ctk.CTkLabel(self.container, text="Place filament on scale and set to 'g'", font=('Arial', 18))
        self.step_label.pack(padx=20, pady=10)

        self.button = ctk.CTkButton(self.container, text='Continue', command=self.get_weight) 
        self.button.pack(padx=20, pady=10)

        self.error_label = ctk.CTkLabel(self.container, text='', text_color='red')
        self.error_label.pack(padx=10, pady=5)

    def get_weight(self):
        result = dm.get_current_weight()

        if isinstance(result, str):
            self.error_label.configure(text=result)
            self.error_label.pack(padx=20, pady=10)
            return None
        
        self.filament_amount = result

        self.show_popup()

    def show_popup(self):
        """ Creates a temporary pop-up message. """
        popup = ctk.CTkToplevel(self)
        popup.title("Update Confirmation")
        popup.geometry("300x100")  # Set popup size

        barcode = self.master.shared_data[barcode]
        data = dm.decode_barcode()
        filament_amount = self.filament_amount
        attributes = " ".join(filter(None, [data[3], data[4]]))

        result = ld.log_filament_data(barcode, filament_amount)

        if result:
            self.error_label.configure(text=result)

        message = f"""
            Updated
            Barcode: {barcode},
            Brand: {data[0]},
            Color: {data[1]},
            Material: {data[2]},
            Attributes: {attributes},
            New Filament Amount: {filament_amount}
            Location: {data[5]}
        """
        
        label = ctk.CTkLabel(popup, text=message, font=("Arial", 14))
        label.pack(pady=20, padx=10)

        # Automatically close the popup after 3 seconds and switch frames
        self.after(5000, lambda: (popup.destroy(), self.master.show_frame('UserScreen')))