import customtkinter as ctk
from screens import *

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
        self.add_frame(UpdateWeightScreen, 'UpdateWeightScreen')
        self.add_frame(NewRollScreen, 'NewRollScreen')

        # Debug mode that creates a dropdown to the side of all the different
        # frames to iterate through without running the program properly
        self.debug_mode = debug_mode
        if self.debug_mode:
            self.frame_selector = ctk.CTkOptionMenu(
                self,
                values=list(self.frames.keys()),
                command=self.show_frame,
            )
            self.frame_selector.grid(row=1, column=1, padx=10, pady=10, sticky='e')

        self.show_frame('UserScreen')

        # Show the first frame 'Login'
        self.change_screen = False  # Track current screen
        self.bind('<Control-Shift-A>', self.toggle_screen) 

    def add_frame(self, page_class, name):
        # Add frames to dictionary and pass class and name and position when displayed
        frame = page_class(self)
        self.frames[name] = frame
        frame.grid(row=1, column=0, sticky='nsew')

    def show_frame(self, name):
        # Show the frame listed
        frame = self.frames[name]
        frame.tkraise()

    def toggle_screen(self, event=None):
        self.change_screen = not self.change_screen  # Toggle between True/False
        new_screen = 'AdminScreen' if self.change_screen else 'UserScreen'
        self.show_frame(new_screen)

# If main then run with debugger
if __name__ == '__main__':
    app = FrameManager(debug_mode=True)
    app.mainloop()