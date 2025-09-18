import os
import sys
import tkinter as tk
from tkinter import PhotoImage
import Login
import LocalDatabase

# #7393B3 - blue gray (background)
# current discounts - save10 - 10% off everything
                    # f150save - $1000 off f150

# get file path for image
def resourcePath(relativePath):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relativePath)

root = tk.Tk()
root.title("Cars-2-U")

iconPath = resourcePath("Images/Logo.png")

try:
    icon = PhotoImage(file=iconPath)
    root.iconphoto(False, icon)
except Exception as e:
    print(f"Error loading icon: {e}")

rootWidth = 1000
rootHeight = 650

# Screen dimensions
screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()

# Calculate center position
xPos = (screenWidth // 2) - (rootWidth // 2)
yPos = (screenHeight // 2) - (rootHeight // 2)

# Set window geometry
root.geometry(f"{rootWidth}x{rootHeight}+{xPos}+{yPos}")

LocalDatabase.createLocalDatabase()

Login.loginPage(root)


root.mainloop()