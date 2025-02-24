import customtkinter as ctk

class UserScreen(ctk.CTkFrame):
    def __init__(self, master, ):
        super().__init__(master)

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True)

        self.label = ctk.CTkLabel(self.container, text='Filament Inventory', font=('Arial', 25))
        self.label.pack(padx=20, pady=10)