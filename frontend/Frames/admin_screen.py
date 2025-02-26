import customtkinter as ctk

class AdminScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True)

        self.label = ctk.CTkLabel(self.container, text='Add New Filament', font=('Arial', 16))
        self.label.pack(padx=20, pady=10)
