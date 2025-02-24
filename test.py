import customtkinter as ctk

def show_admin_page(event=None):
    frame_main.pack_forget()
    frame_admin.pack(fill="both", expand=True)

def show_main_page(event=None):
    frame_admin.pack_forget()
    frame_main.pack(fill="both", expand=True)

# Main window
app = ctk.CTk()
app.geometry("600x400")
app.title("App")

# Main page
frame_main = ctk.CTkFrame(app)
frame_main.pack(fill="both", expand=True)
label_main = ctk.CTkLabel(frame_main, text="Main Page")
label_main.pack(pady=20)

# Admin page
frame_admin = ctk.CTkFrame(app)
label_admin = ctk.CTkLabel(frame_admin, text="Admin Page")
label_admin.pack(pady=20)
button_back = ctk.CTkButton(frame_admin, text="Back", command=show_main_page)
button_back.pack()

# Key bindings
app.bind("<Control-Shift-A>", show_admin_page)

app.mainloop()
