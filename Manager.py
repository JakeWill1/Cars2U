import tkinter as tk
from tkinter import ttk
import Helper as h
import Login
import Help
import UpdateInventory
import Restock
import DBLibrary as db
import ManageAccounts
import PromoCodes
import ShowReports
import CustomerLookup

def managerPage(window, personID):
    """
    Displays the Manager Page UI with navigation buttons to key manager tools.

    This page allows the manager to:
    - Update inventory
    - Restock items
    - Manage user accounts
    - Add promotional codes
    - View and print reports
    - Access the point-of-sale system
    - Return to login
    - Access help

    Args:
        window (tk.Tk): The root Tkinter window.
        personID (int): The PersonID of the logged-in manager.
    """
    window.configure(background="#7393B3")
    titleLabel = ttk.Label(window, text="Manager Page", font=("Calibri", 48, "bold"), background="#7393B3")
    titleLabel.place(relx=0.5, rely=0.2, anchor="center")

    buttonFrame = tk.Frame(window, bg="#7393B3")
    buttonFrame.place(relx=0.5, rely=0.5, anchor="center")

    def back():
        """
        Returns the user to the login screen.
        """
        h.clearScreen(window)
        Login.loginPage(window)

    def updateInventory():
        """
        Navigates to the Update Inventory page.
        """
        h.clearScreen(window)
        UpdateInventory.updateInventoryPage(window, personID)

    def restockInventory():
        """
        Navigates to the Restock Inventory page.
        """
        h.clearScreen(window)
        Restock.restockPage(window, personID)

    def manageAccounts():
        """
        Navigates to the Manage Accounts page.
        """
        h.clearScreen(window)
        ManageAccounts.manageAccountsPage(window, personID)

    def addPromo():
        """
        Navigates to the Add Promo Codes page.
        """
        h.clearScreen(window)
        PromoCodes.promoCodesPage(window, personID)

    def viewReports():
        """
        Opens the View/Print Reports page to generate customer or sales reports.
        """
        h.clearScreen(window)
        ShowReports.showReportsPage(window, personID)

    def pos():
        """
        Opens the Point-of-Sale system for checking out customers.
        """
        h.clearScreen(window)
        CustomerLookup.customerLookupPage(window, personID)

    ttk.Button(buttonFrame, text="Update Inventory", command=updateInventory, width=30).pack(pady=10)
    ttk.Button(buttonFrame, text="Inventory Restock", command=restockInventory, width=30).pack(pady=10)
    ttk.Button(buttonFrame, text="Manage Accounts", command=manageAccounts, width=30).pack(pady=10)
    ttk.Button(buttonFrame, text="Add Promo Codes", command=addPromo, width=30).pack(pady=10)
    ttk.Button(buttonFrame, text="View/Print Reports", command=viewReports, width=30).pack(pady=10)
    ttk.Button(buttonFrame, text="Point of Sale", command=pos, width=30).pack(pady=10)

    backButton = ttk.Button(window, text="Back", command=back)
    backButton.place(relx=0.9, rely=0.95, anchor="s")

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("Manager"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")

    db.checkLowInventory()