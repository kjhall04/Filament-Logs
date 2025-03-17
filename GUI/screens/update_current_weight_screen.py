import customtkinter as ctk

class UpdateCurrentWeightScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True)

        self.title_label = ctk.CTkLabel(self.container, text='-- Update Weight --', font=('Arial', 14))
        self.title_label.pack(padx=20, pady=10)

        self.step_label = ctk.CTkLabel(self.container, text="Place filament on scale and set to 'g'", font=('Arial', 18))
        self.step_label.pack(padx=20, pady=10)

        self.button = ctk.CTkButton(self.container, text='Continue', command=None) 
        self.button.pack(padx=20, pady=10)