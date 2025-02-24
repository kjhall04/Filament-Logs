import customtkinter as ctk

class AdminScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True)

        self.label = ctk.CTkLabel(self.container, text='Admin', font=('Arial', 25))
        self.label.pack(padx=20, pady=10)

        self.back_button = ctk.CTkButton(self.container, text='Back', command=lambda: self.master.show_frame('UserScreen'))
        self.back_button.pack(padx=20, pady=5)
