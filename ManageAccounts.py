import tkinter as tk
from tkinter import ttk, messagebox
import DBLibrary as db
import Helper as h
import Manager
import Help
import ManageUser
import Register

def manageAccountsPage(window, personID):
    """
    Displays the Manage Accounts page for a manager user.
    
    This page allows the manager to:
    - View all user accounts in a treeview table
    - Disable selected accounts
    - Add or update user accounts
    - Navigate back to the Manager page
    - Access Help

    Args:
        window (tk.Tk): The main application window.
        personID (int): The PersonID of the currently logged-in manager.
    """
    window.configure(background="#7393B3")

    titleLabel = ttk.Label(window, text="Manage Accounts", font=("Calibri", 32, "bold"), background="#7393B3")
    titleLabel.pack(pady=20)

    # Treeview
    columns = ("PersonID", "Username", "Position", "Account Disabled", "Account Deleted")
    tree = ttk.Treeview(window, columns=columns, show="headings")

    columnWidths = {
        "PersonID": 80,
        "Username": 200,
        "Position": 120,
        "Account Disabled": 120,
        "Account Deleted": 120
    }

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=columnWidths[col], anchor="center")

    tree.pack(pady=10)

    def loadAccounts():
        """
        Loads all user accounts from the database and populates the treeview.
        Displays a message row if no accounts are found.
        """
        accounts = db.getAllAccounts()

        tree.delete(*tree.get_children())

        if not accounts:
            tree.insert("", "end", values=("", "No accounts found.", "", "", ""))
            return

        for account in accounts:
            tree.insert("", "end", values=(
                account['PersonID'],
                account['Username'],
                account['Position'],
                "Yes" if account['AccountDisabled'] else "No",
                "Yes" if account['AccountDeleted'] else "No"
            ))

    def disableAccount():
        """
        Disables the selected account in the treeview by updating the database.
        Displays a warning if no account is selected.
        """
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an account to disable.")
            return
        personID = tree.item(selected)['values'][0]
        db.disableAccount(personID)
        loadAccounts()

    loadAccounts()

    buttonFrame = tk.Frame(window, background="#7393B3")
    buttonFrame.pack(pady=15)

    def back():
        """
        Returns the user to the Manager main page.
        """
        h.clearScreen(window)
        Manager.managerPage(window, personID)

    def addAccount():
        """
        Opens the account creation or update page:
        - If an account is selected, opens ManageUser page to update.
        - If nothing is selected, opens Register page to add new user.
        """
        selected = tree.focus()
        if selected:
            personIDSelected = tree.item(selected)['values'][0]
            h.clearScreen(window)
            ManageUser.manageUserPage(window, personID, personIDSelected)
        else:
            h.clearScreen(window)
            Register.registerPage(window, True, personID)

    backButton = ttk.Button(buttonFrame, text="Back", command=back)
    backButton.pack(side="left", padx=10)

    disableButton = ttk.Button(buttonFrame, text="Disable Account", command=disableAccount)
    disableButton.pack(side="left", padx=10)

    addAccountButton = ttk.Button(buttonFrame, text="Add/Update Account", command=lambda: addAccount())
    addAccountButton.pack(side="left", padx=10)


    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("ManageAccounts"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")
