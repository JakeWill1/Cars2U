import tkinter as tk
from tkinter import ttk
import DBLibrary as db
import Helper as h
import Manager
import Help

def restockPage(window, personID):
    """
    Displays the restock notification page for managers.

    Shows a table of items that have low inventory levels based on their restock threshold.
    Includes buttons for refreshing the table, going back to the manager page, and opening the help page.

    Args:
        window (tk.Tk or tk.Frame): The main application window or frame.
        personID (int): The ID of the manager accessing the page.
    """
    window.configure(background="#7393B3")

    titleLabel = ttk.Label(window, text="Restock Notification", font=("Calibri", 32, "bold"), background="#7393B3")
    titleLabel.pack(pady=20)

    columns = ("ID", "Name", "Current Quantity", "Restock Threshold")
    tree = ttk.Treeview(window, columns=columns, show="headings")

    columnWidths = {
        "ID": 50,
        "Name": 250,
        "Current Quantity": 150,
        "Restock Threshold": 150
    }

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=columnWidths[col], anchor="center")

    tree.pack(pady=10)

    def loadRestockItems():
        """
        Loads all inventory items that are below their restock threshold.

        Retrieves the list from the database and populates the Treeview table.
        If no items are low in stock, a message row is shown instead.
        """
        items = db.getLowInventoryItems()

        tree.delete(*tree.get_children())

        if not items:
            tree.insert("", "end", values=("", "No low stock items found.", "", ""))
            return

        for item in items:
            tree.insert("", "end", values=(
                item['InventoryID'],
                item['ItemName'],
                item['Quantity'],
                item['RestockThreshold']
            ))

    loadRestockItems()
    
    buttonFrame = tk.Frame(window, background="#7393B3")
    buttonFrame.pack(pady=15)

    def back():
        """
        Clears the current screen and navigates back to the manager main page.
        """
        h.clearScreen(window)
        Manager.managerPage(window, personID)

    backButton = ttk.Button(buttonFrame, text="Back", command=back)
    backButton.pack(side="left", padx=10)

    refreshButton = ttk.Button(buttonFrame, text="Refresh", command=loadRestockItems)
    refreshButton.pack(side="left", padx=10)

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("RestockPage"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")