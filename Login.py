import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import Register
import ForgotPassword
import DBLibrary as db
import Helper as h
import Customer
import Manager
import Help

def resourcePath(relativePath):
    """
    Returns the absolute path to a resource.

    Args:
        relativePath (str): The relative path to the resource.

    Returns:
        str: The full path to the resource file.
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relativePath)

def loginPage(window):
    """
    Sets up and displays the login page UI inside the given Tkinter window.

    Args:
        window (tk.Tk): The root Tkinter window where the login UI is displayed.
    """

    window.configure(background="#7393B3")

    logoPath = resourcePath("Images/Logo.png")
    try:
        logo = Image.open(logoPath)
        logo = logo.resize((100, 100), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(logo)
    except Exception as e:
        print(f"Error loading logo in login: {e}")
        
    logoLabel = ttk.Label(window, image=photo, background="#7393B3")
    logoLabel.place(relx=0.65, rely=0.2, anchor="center")
    logoLabel.image = photo

    companyLabel = ttk.Label(window, text="Cars-2-U", font=("Calibri", 48, "bold"), background="#7393B3")
    companyLabel.place(relx=0.45, rely=0.2, anchor="center")

    def togglePass():
        """
        Toggles the password field visibility between masked and plain text.
        """
        if passInput.cget("show") == "*":
            passInput.config(show="")
            showPass.config(text="Hide")
        else:
            passInput.config(show="*")
            showPass.config(text="Show")

    def tryLogin():
        """
        Attempts to log in the user based on entered credentials.
        Redirects to Customer or Manager page on success, 
        shows warning on failure.
        """
        name = userInput.get()
        password = passInput.get()

        result, personID = db.testLogin(name, password)
        
        if (result == 1):
            h.clearScreen(window)
            Customer.customerPage(window, personID, 0)
        elif (result == 2):
            h.clearScreen(window)
            Manager.managerPage(window, personID)
        else:
            userInput.delete(0, tk.END)
            passInput.delete(0, tk.END)
            messagebox.showwarning(title="Invalid Credentials", message="Username or password do not match!")

    def register():
        """
        Redirects the user to the registration page.
        """
        h.clearScreen(window)
        Register.registerPage(window, False)

    def forgotPassword():
        """
        Initiates password reset process if username exists in the database.
        Prompts the user to enter a username if not provided.
        """
        username = userInput.get()
        if not username:
            messagebox.showwarning(title="Invalid Username", message="Please enter your username to reset password")
            return
        exists = db.userExists(username)
        if exists:
            h.clearScreen(window)
            ForgotPassword.forgotPasswordPage(window, username)

    def guest():
        """
        Opens the Customer page as a guest user (no login required).
        """
        h.clearScreen(window)
        Customer.customerPage(window, None, 0)

    # Main Frame
    mainFrame = ttk.Frame(window, padding="30 30 30 30")
    mainFrame.place(relx=0.5, rely=0.5, anchor="center")

    # Title
    titleLabel = ttk.Label(mainFrame, text="Please Log In", font=("Calibri", 24, "bold"))
    titleLabel.grid(column=0, row=0, columnspan=2, pady=(0, 20))

    # Username
    userLabel = ttk.Label(mainFrame, text="Username")
    userLabel.grid(column=0, row=1, sticky="W", pady=5)

    userInput = ttk.Entry(mainFrame, width=25)
    userInput.grid(column=1, row=1, pady=5)

    # Password
    passLabel = ttk.Label(mainFrame, text="Password")
    passLabel.grid(column=0, row=2, sticky="W", pady=5)

    passInput = ttk.Entry(mainFrame, width=25, show="*")
    passInput.grid(column=1, row=2)

    showPass = ttk.Button(mainFrame, text="Show", command=togglePass, width=5)
    showPass.grid(column=2, row=2)

    # Buttons Frame
    buttonsFrame = ttk.Frame(mainFrame)
    buttonsFrame.grid(column=0, row=4, columnspan=2, pady=10)

    loginButton = ttk.Button(buttonsFrame, text="Login", command=tryLogin)
    loginButton.grid(column=0, row=0, padx=5)

    registerButton = ttk.Button(buttonsFrame, text="Register", command=register)
    registerButton.grid(column=1, row=0, padx=5)

    forgotButton = ttk.Button(buttonsFrame, text="Forgot Password", command=forgotPassword)
    forgotButton.grid(column=2, row=0, padx=5)

    guestButton = ttk.Button(buttonsFrame, text="Guest", command=guest)
    guestButton.grid(column=2, row=1, padx=5)

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("Login"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")