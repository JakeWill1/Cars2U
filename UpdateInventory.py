import tkinter as tk
from tkinter import ttk, messagebox
import DBLibrary as db
import Helper as h
import Manager
import Help
import AddInventory

def updateInventoryPage(window, personID):
    """
    Displays the Update Inventory page for managers.

    Allows searching, viewing, updating, and removing inventory items.
    Includes functionality for:
        - Searching for inventory items by keyword
        - Adding or updating a selected product
        - Marking a product as discontinued
        - Updating product quantity
        - Navigating back to the manager page
        - Opening the help page

    Args:
        window (tk.Tk or tk.Frame): The main application window or frame.
        personID (int): The ID of the manager currently logged in.
    """
    window.configure(background="#7393B3")

    titleLabel = ttk.Label(window, text="Update Inventory", font=("Calibri", 32, "bold"), background="#7393B3")
    titleLabel.pack(pady=20)

    # Search bar
    searchFrame = ttk.Frame(window)
    searchFrame.pack(pady=5)

    searchEntry = ttk.Entry(searchFrame, width=50)
    searchEntry.pack(side="left", padx=5)

    def searchInventory():
        """
        Searches inventory based on the keyword entered in the search bar.

        If the input is empty, no results are shown.
        Populates the tree view with search results.
        """
        keyword = searchEntry.get().strip()
        if keyword:
            items = db.searchInventoryManager(keyword)
        else:
            items = []
        refreshTree(items)

    searchButton = ttk.Button(searchFrame, text="Search", command=searchInventory)
    searchButton.pack(side="left", padx=5)

    # Treeview to display inventory
    columns = ("ID", "Name", "Cost", "Retail Price", "Quantity", "Restock Threshold","Discontinued")
    tree = ttk.Treeview(window, columns=columns, show="headings")
    columnWidths = {
        "ID": 50,
        "Name": 200,
        "Cost": 100,
        "Retail Price": 100,
        "Quantity": 80,
        "Restock Threshold": 120,
        "Discontinued": 100
    }

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=columnWidths[col], anchor="center")
    tree.pack(pady=10)


    def refreshTree(items):
        """
        Clears and repopulates the tree view with the given inventory items.

        Args:
            items (list): List of inventory item dictionaries to display.
        """
        if not items:
            tree.delete(*tree.get_children())
            tree.insert("", "end", values=("", "No matching products found", "", "", "", ""))
            return
    
        tree.delete(*tree.get_children())
        for item in items:
            tree.insert("", "end", values=(
                item['InventoryID'],
                item['ItemName'],
                f"${item['Cost']:.2f}",
                f"${item['RetailPrice']:.2f}",
                item['Quantity'],
                item['RestockThreshold'],
                "Yes" if item['Discontinued'] else "No"
            ))

    def back():
        """
        Clears the current screen and navigates back to the manager main page.
        """
        h.clearScreen(window)
        Manager.managerPage(window, personID)

    def addProduct():
        """
        Opens the Add/Update Inventory page.

        If an item is selected in the tree view, loads that item for editing.
        Otherwise, opens the form to add a new product.
        """
        selected = tree.focus()
        if not selected:
            h.clearScreen(window)
            AddInventory.addInventoryPage(window, personID)
        else:
            itemID = tree.item(selected)['values'][0]
            h.clearScreen(window)
            AddInventory.addInventoryPage(window, personID, itemID)

    def removeProduct():
        """
        Sets the selected product as discontinued in the database.

        If no product is selected, the function does nothing.
        Refreshes the tree view after removal.
        """
        selected = tree.focus()
        if not selected:
            return
        itemID = tree.item(selected)['values'][0]
        # Set item as discontinued
        db.removeItem(itemID)
        searchInventory()

    def updateQuantity():
        """
        Updates the quantity of the selected product with the entered value.

        Shows an error message if the input is not a valid non-negative integer.
        Refreshes the tree view after a successful update.
        """
        selected = tree.focus()
        if not selected:
            return
        try:
            qty = int(qtyEntry.get().strip())
            if qty < 0:
                raise ValueError
            itemID = tree.item(selected)['values'][0]
            db.updateInventoryQuantity(itemID, qty)
            searchInventory()
            qtyEntry.delete(0, tk.END)
        except:
            messagebox.showerror("Invalid Quantity", "Please enter a valid non-negative quantity.")

    # Quantity controls
    controlFrame = ttk.Frame(window)
    controlFrame.pack(pady=10)

    qtyEntry = ttk.Entry(controlFrame, width=5)
    qtyEntry.pack(side="left", padx=5)

    updateButton = ttk.Button(controlFrame, text="Update Quantity", command=updateQuantity)
    updateButton.pack(side="left", padx=5)

    removeButton = ttk.Button(controlFrame, text="Remove Product", command=removeProduct)
    removeButton.pack(side="left", padx=5)

    addButton = ttk.Button(controlFrame, text="Add/Update Product", command=addProduct)
    addButton.pack(side="left", padx=5)

    # Navigation buttons
    buttonFrame = tk.Frame(window, bg="#7393B3")
    buttonFrame.pack(pady=10)

    backButton = ttk.Button(buttonFrame, text="Back", command=back)
    backButton.pack(side="left", padx=10)

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("UpdateInventory"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")