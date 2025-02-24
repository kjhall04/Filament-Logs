import customtkinter as ctk
from frontend.Frames import *

# Set the default appearance of the GUI to dark mode and the colors to green
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('green')

# Class to run all frames through
class FrameManager(ctk.CTk):
    def __init__(self, debug_mode=False):
        super().__init__()
        
        # Program title and screen size
        self.title('Filament Inventory')
        self.geometry(f"{1100}x{580}")

        # Configure layout grid
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title label that stays fixed at the top
        self.title_label = ctk.CTkLabel(self, text='-- Filament Inventory --', font=('Arial', 28, 'bold'))
        self.title_label.grid(row=0, column=0, pady=10)

        # Create a dictionary for frames
        self.frames = {}

        # Add all the frames by class and name for reference
        self.add_frame(UserScreen, 'UserScreen')
        self.add_frame(AdminScreen, 'AdminScreen')

        # Debug mode that creates a dropdown to the side of all the different
        # frames to iterate through without running the program properly
        self.debug_mode = debug_mode
        if self.debug_mode:
            self.frame_selector = ctk.CTkOptionMenu(
                self,
                values=list(self.frames.keys()),
                command=self.show_frame,
            )
            self.frame_selector.grid(row=0, column=1, padx=10, pady=10, sticky='e')

        # Show the first frame 'Login'
        self.show_frame('UserScreen')

        # Keybinding for switching to AdminScreen
        self.bind('<Control-Shift-A>', lambda event: self.show_frame('AdminScreen'))

    def add_frame(self, page_class, name):
        # Add frames to dictionary and pass class and name and position when displayed
        frame = page_class(self)
        self.frames[name] = frame
        frame.grid(row=1, column=0, sticky='nsew')

    def show_frame(self, name):
        # Show the frame listed
        frame = self.frames[name]
        frame.tkraise()

# If main then run with debugger
if __name__ == '__main__':
    app = FrameManager(debug_mode=True)
    app.mainloop()