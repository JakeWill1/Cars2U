import tkinter as tk
from tkinter import ttk, messagebox
import Helper as h
import DBLibrary as db
import datetime
import Help

def showReportsPage(window, personID):
    """
    Displays the Reports Center page for managers.

    Provides tabs for generating different types of sales and inventory reports.
    Sales reports can be generated based on a daily, weekly, or monthly date.
    Inventory reports can be filtered by type (for sale, needing restock, or all).

    Args:
        window (tk.Tk or tk.Frame): The application window or container to populate with the report UI.
        personID (int): The ID of the logged-in manager for navigation purposes.
    """
    window.configure(background="#7393B3")
    h.clearScreen(window)

    titleLabel = ttk.Label(window, text="Reports Center", font=("Calibri", 36, "bold"), background="#7393B3")
    titleLabel.pack(pady=20)

    mainFrame = ttk.Frame(window)
    mainFrame.pack(pady=10)

    notebook = ttk.Notebook(mainFrame)
    notebook.pack()

    salesTab = ttk.Frame(notebook)
    inventoryTab = ttk.Frame(notebook)

    notebook.add(salesTab, text="Sales Reports")
    notebook.add(inventoryTab, text="Inventory Reports")

    salesOptionVar = tk.StringVar(value="daily")

    ttk.Label(salesTab, text="Select Report Type:").pack(pady=5)

    ttk.Radiobutton(salesTab, text="Daily", variable=salesOptionVar, value="daily").pack()
    ttk.Radiobutton(salesTab, text="Weekly", variable=salesOptionVar, value="weekly").pack()
    ttk.Radiobutton(salesTab, text="Monthly", variable=salesOptionVar, value="monthly").pack()

    dateVar = tk.StringVar()

    ttk.Label(salesTab, text="Enter Date (MM/DD/YYYY or MM/YYYY for monthly)").pack(pady=5)
    dateEntry = ttk.Entry(salesTab, textvariable=dateVar, width=20)
    dateEntry.pack()

    def generateSalesReport():
        """
        Generates a sales report based on the selected frequency and date input.

        The frequency can be daily, weekly, or monthly, and the corresponding
        helper function is called with the appropriate date format.
        Displays an error message if the input date is missing or incorrectly formatted.
        """
        selection = salesOptionVar.get()
        dateInput = dateVar.get().strip()

        if not dateInput:
            messagebox.showerror("Input Error", "Please enter a valid date.")
            return

        try:
            if selection == "daily":
                dateObj = datetime.datetime.strptime(dateInput, "%m/%d/%Y")
                h.generateDailySalesReport(dateObj.date())
            elif selection == "weekly":
                dateObj = datetime.datetime.strptime(dateInput, "%m/%d/%Y")
                h.generateWeeklySalesReport(dateObj.date())
            elif selection == "monthly":
                dateObj = datetime.datetime.strptime(dateInput, "%m/%Y")
                h.generateMonthlySalesReport(dateObj.month, dateObj.year)
        except ValueError:
            messagebox.showerror("Date Error", "Please enter a valid date format.")

    ttk.Button(salesTab, text="Generate Sales Report", command=generateSalesReport).pack(pady=10)

    inventoryOptionVar = tk.StringVar(value="forsale")

    ttk.Label(inventoryTab, text="Select Inventory Report Type:").pack(pady=5)

    ttk.Radiobutton(inventoryTab, text="Items For Sale", variable=inventoryOptionVar, value="forsale").pack()
    ttk.Radiobutton(inventoryTab, text="Items Needing Restock", variable=inventoryOptionVar, value="restock").pack()
    ttk.Radiobutton(inventoryTab, text="All Items", variable=inventoryOptionVar, value="all").pack()

    def generateInventoryReport():
        """
        Generates an inventory report based on the selected type.

        The type can be:
            - Items currently for sale
            - Items below restock threshold
            - All inventory items

        Calls the corresponding helper function to generate the report.
        """
        selection = inventoryOptionVar.get()

        if selection == "forsale":
            h.generateInventoryReportForSale()
        elif selection == "restock":
            h.generateInventoryReportRestock()
        elif selection == "all":
            h.generateInventoryReportAll()

    ttk.Button(inventoryTab, text="Generate Inventory Report", command=generateInventoryReport).pack(pady=10)

    def back():
        """
        Clears the current screen and navigates back to the manager main page.
        """
        h.clearScreen(window)
        import Manager
        Manager.managerPage(window, personID)

    backButton = ttk.Button(window, text="Back", command=back)
    backButton.place(relx=0.9, rely=0.95, anchor="s")

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("Reports"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")
