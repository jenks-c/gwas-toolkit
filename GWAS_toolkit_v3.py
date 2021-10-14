print("***GWAS Plots***")
print("Importing Modules...")

import tkinter as tk

from assoc_interface_application import Application

print("Starting App...")

root = tk.Tk()
root.title("GWAS Toolkit v3.2")
width  = root.winfo_screenwidth()
height = root.winfo_screenheight()
try:
    root.state("zoomed")
except:
    try:
        root.attributes('-zoomed', True)
    except:
        print("Error, could not maximise screen")
root["background"] = "darkslategrey"
app = Application(master=root)
app.mainloop()

