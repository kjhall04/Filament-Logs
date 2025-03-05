import customtkinter as ctk

class AdminScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, padx=20, pady=20)

        self.label = ctk.CTkLabel(self.container, text='Admin Functions', font=('Arial', 16))
        self.label.grid(column=0, row=0, columnspan=2, padx=20, pady=10)

        self.add_button = ctk.CTkButton(self.container, text='Add Filament', command=lambda: self.master.show_frame('NewRollScreen'))
        self.add_button.grid(column=0, row=1, padx=(20, 10), pady=20)

        self.stats_button = ctk.CTkButton(self.container, text='Stats', command=None)
        self.stats_button.grid(column=1, row=1, padx=(10, 20), pady=20)