import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import DBLibrary as db
import Helper as h
import Manager
import Help
import os

def manageUserPage(window, personID, selectedPersonID=None):
    """
    Displays the Manage User Profile page where managers can view and update 
    user information including personal details, login credentials, and account position.

    Args:
        window (tk.Tk): The root application window where the UI is rendered.
        personID (int): The manager's PersonID (used to return to Manager page).
        selectedPersonID (int, optional): The PersonID of the user being managed (if None, a new user is being created).
    """
    window.configure(background="#7393B3")

    titleLabel = ttk.Label(window, text="Manage User Profile", font=("Calibri", 32, "bold"), background="#7393B3")
    titleLabel.pack(pady=20)

    contentFrame = ttk.Frame(window)
    contentFrame.pack(pady=10)

    formFrame = ttk.Frame(contentFrame)
    formFrame.pack(side="left", padx=20, pady=10)

    loginFrame = ttk.Frame(contentFrame)
    loginFrame.pack(side="right", padx=20, pady=10)

    fields = [
        ("Title", tk.StringVar()),
        ("First Name", tk.StringVar()),
        ("Middle Name", tk.StringVar()),
        ("Last Name", tk.StringVar()),
        ("Suffix", tk.StringVar()),
        ("Address 1", tk.StringVar()),
        ("Address 2", tk.StringVar()),
        ("Address 3", tk.StringVar()),
        ("City", tk.StringVar()),
        ("Zipcode", tk.StringVar()),
        ("State", tk.StringVar()),
        ("Email", tk.StringVar()),
        ("Phone Primary", tk.StringVar()),
        ("Phone Secondary", tk.StringVar())
    ]

    loginFields = [
        ("Username", tk.StringVar()),
        ("Password", tk.StringVar()),
        ("Security Question 1", tk.StringVar()),
        ("Security Answer 1", tk.StringVar()),
        ("Security Question 2", tk.StringVar()),
        ("Security Answer 2", tk.StringVar()),
        ("Security Question 3", tk.StringVar()),
        ("Security Answer 3", tk.StringVar())
    ]

    entries = {}

    for i, (labelText, var) in enumerate(fields):
        label = ttk.Label(formFrame, text=labelText)
        label.grid(row=i, column=0, pady=3, padx=5, sticky="e")
        entry = ttk.Entry(formFrame, textvariable=var, width=30)
        entry.grid(row=i, column=1, pady=3, padx=5, sticky="w")
        entries[labelText] = var

    positionLabel = ttk.Label(formFrame, text="Position")
    positionLabel.grid(row=len(fields), column=0, pady=3, padx=5, sticky="e")

    positionVar = tk.StringVar()
    positionDropdown = ttk.OptionMenu(formFrame, positionVar, "customer", "customer", "manager")
    positionDropdown.grid(row=len(fields), column=1, pady=3, padx=5, sticky="w")

    imageFrame = ttk.Frame(formFrame)
    imageFrame.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)

    imagePath = tk.StringVar()
    imageNameLabel = ttk.Label(imageFrame, text="No file selected")
    imageNameLabel.pack(side="left", padx=5)

    def browseImage():
        """
        Opens a file dialog for the user to select an image file. 
        Updates the imagePath and label with the selected file.
        """
        filePath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if filePath:
            imagePath.set(filePath)
            imageNameLabel.config(text=os.path.basename(filePath))

    imageButton = ttk.Button(imageFrame, text="Browse Image", command=browseImage)
    imageButton.pack(side="left", padx=5)

    for i, (labelText, var) in enumerate(loginFields):
        label = ttk.Label(loginFrame, text=labelText)
        label.grid(row=i, column=0, pady=3, padx=5, sticky="e")

        if labelText == "Username":
            usernameLabel = ttk.Label(loginFrame, textvariable=var, width=30, anchor="w")
            usernameLabel.grid(row=i, column=1, pady=3, padx=5, sticky="w")
        elif "Question" in labelText:
            questionLabel = ttk.Label(loginFrame, textvariable=var, width=30, anchor="w")
            questionLabel.grid(row=i, column=1, pady=3, padx=5, sticky="w")
        else:
            entry = ttk.Entry(loginFrame, textvariable=var, width=30)
            entry.grid(row=i, column=1, pady=3, padx=5, sticky="w")

        entries[labelText] = var

    if selectedPersonID:
        userInfo = db.getAllUserInfo(selectedPersonID)
        if userInfo:
            for fieldName in entries:
                entries[fieldName].set(userInfo.get(fieldName, ""))
            positionVar.set(userInfo.get("Position", "Customer"))

    def submit():
        """
        Gathers input field data, validates required fields, 
        optionally converts the image to binary, 
        and updates the user profile in the database.
        Returns to the Manager page upon success.
        """
        try:
            data = {field: var.get().strip() for field, var in entries.items()}
            position = positionVar.get()
            img = imagePath.get()

            if not data["First Name"] or not data["Last Name"]:
                raise ValueError("Required fields missing.")

            positionID = 1000 if position == "customer" else 1001

            imageBlob = None
            if img:
                imageBlob = h.convertImageToBlob(img)

            db.updateUserProfile(selectedPersonID, data, positionID, position, imageBlob)
            messagebox.showinfo("Success", "User updated successfully!")

            h.clearScreen(window)
            Manager.managerPage(window, personID)

        except Exception as e:
            print(f"Error saving user: {e}")
            messagebox.showerror("Error", "Please ensure all fields are filled correctly.")

    buttonFrame = tk.Frame(window, background="#7393B3")
    buttonFrame.pack(pady=15)

    backButton = ttk.Button(buttonFrame, text="Back", command=lambda: back())
    backButton.pack(side="left", padx=10)

    submitButton = ttk.Button(buttonFrame, text="Update", command=submit)
    submitButton.pack(side="left", padx=10)

    def back():
        """
        Clears the screen and navigates back to the Manager page.
        """
        h.clearScreen(window)
        Manager.managerPage(window, personID)

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("ManageUser"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")