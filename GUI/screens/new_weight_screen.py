import customtkinter as ctk
import data_manipulation as dm

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