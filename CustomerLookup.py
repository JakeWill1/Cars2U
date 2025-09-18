import tkinter as tk
from tkinter import ttk, messagebox
import Helper as h
import DBLibrary as db
import Help
import Manager
import Customer

def customerLookupPage(window, managerID):
    """
    Displays the Customer Lookup page for a manager.

    This page allows the manager to:
    - Search for customers using different fields
    - View customer orders
    - Select a customer to enter the customer-facing POS interface
    - Return to the Manager main page

    Args:
        window (tk.Tk): The main Tkinter window to populate the page.
        managerID (int): The PersonID of the logged-in manager.
    """
    window.configure(background="#7393B3")
    h.clearScreen(window)

    def searchCustomers():
        """
        Searches for customers in the database based on the selected method and search keyword.
        Displays results in the customer result tree.
        """
        keyword = searchVar.get().strip()
        method = methodVar.get()

        if not keyword:
            messagebox.showerror("Input Error", "Please enter a search value.")
            return

        resultTree.delete(*resultTree.get_children())

        results = db.searchCustomerPOS(keyword, method)
        for customer in results:
            resultTree.insert("", "end", iid=customer['PersonID'],
                              values=(customer['PersonID'], customer['FirstName'], customer['LastName'], customer['Email'], customer['Phone']))

    def selectCustomer():
        """
        Loads the selected customer into the Customer Page POS interface.
        """
        selected = resultTree.focus()
        if not selected:
            messagebox.showerror("Selection Error", "Please select a customer.")
            return
        personID = int(selected)
        h.clearScreen(window)
        Customer.customerPage(window, personID, 0, managerID)

    def showCustomerOrders():
        """
        Displays all orders for the selected customer in the orders tree view.
        """
        selected = resultTree.focus()
        if not selected:
            messagebox.showerror("Selection Error", "Please select a customer.")
            return
        personID = int(selected)
        ordersTree.delete(*ordersTree.get_children())
        orders = db.getOrdersByCustomer(personID)
        for order in orders:
            ordersTree.insert("", "end", values=(
                order['OrderID'],
                order['InventoryID'],
                order['Quantity'],
                order['DiscountID'],
                order['OrderDate']
            ))

    def back():
        """
        Navigates back to the Manager Page.
        """
        h.clearScreen(window)
        Manager.managerPage(window, managerID)

    titleLabel = ttk.Label(window, text="Customer Lookup", font=("Calibri", 36, "bold"), background="#7393B3")
    titleLabel.pack(pady=20)

    searchFrame = tk.Frame(window, background="#7393B3")
    searchFrame.pack()

    searchVar = tk.StringVar()
    methodVar = tk.StringVar(value="Email")

    ttk.Label(searchFrame, text="Search Value:", background="#7393B3").grid(row=0, column=0, padx=5, pady=5)
    searchEntry = ttk.Entry(searchFrame, textvariable=searchVar, width=30)
    searchEntry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(searchFrame, text="Search By:", background="#7393B3").grid(row=1, column=0, padx=5, pady=5)
    searchOptions = ["First Name", "Last Name", "Email", "Phone", "Invoice", "MemberID"]
    searchDropdown = ttk.OptionMenu(searchFrame, methodVar, searchOptions[0], *searchOptions)
    searchDropdown.grid(row=1, column=1, padx=5, pady=5)

    actionFrame = tk.Frame(window, background="#7393B3")
    actionFrame.pack()

    ttk.Button(actionFrame, text="Search", command=searchCustomers).pack(side="left", padx=5)
    ttk.Button(actionFrame, text="Customer Orders", command=showCustomerOrders).pack(side="left", padx=5)
    ttk.Button(actionFrame, text="Select Customer", command=selectCustomer).pack(side="left", padx=5)

    resultTree = ttk.Treeview(window, columns=("PersonID", "FirstName", "LastName", "Email", "Phone"), show="headings", height=5)
    for col in resultTree["columns"]:
        resultTree.heading(col, text=col)
    resultTree.pack(pady=10, fill="both", expand=True)

    ordersTree = ttk.Treeview(window, columns=("OrderID", "InventoryID", "Quantity", "DiscountID", "OrderDate"), show="headings", height=5)
    for col in ordersTree["columns"]:
        ordersTree.heading(col, text=col)
    ordersTree.pack(pady=10, fill="both", expand=True)

    backButton = ttk.Button(window, text="Back", command=back)
    backButton.place(relx=0.9, rely=0.1, anchor="s")

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("CustomerLookup"))
    helpButton.place(relx=0.05, rely=0.1, anchor="sw")
