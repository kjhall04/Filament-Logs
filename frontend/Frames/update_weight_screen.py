import customtkinter as ctk

class UpdateWeightScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True)

        self.step1_label = ctk.CTkLabel(self.container, text='Place filament on scale...', font=('Arial', 16))
        self.step1_label.pack(padx=20, pady=10)

        self.step2_label = ctk.CTkLabel(self.container, text="Press 'Enter' to continue", font=('Arial', 16)) 
        self.step2_label.pack(padx=20, pady=10)