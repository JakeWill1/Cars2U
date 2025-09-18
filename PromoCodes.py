import tkinter as tk
from tkinter import ttk, messagebox
import Helper as h
import DBLibrary as db
import Manager
import Help

def promoCodesPage(window, personID):
    """
    Displays the manager page for managing promotional codes. Allows creating, 
    searching, viewing, and deleting promo codes with support for cart-level and item-level discounts.

    Args:
        window (tk.Tk or tk.Frame): The root window or frame where the UI is displayed.
        personID (int): ID of the currently logged-in manager.
    """
    window.configure(background="#7393B3")
    h.clearScreen(window)

    titleLabel = ttk.Label(window, text="Manage Promo Codes", font=("Calibri", 36, "bold"), background="#7393B3")
    titleLabel.pack(pady=20)

    mainFrame = ttk.Frame(window)
    mainFrame.pack(padx=10, pady=10, fill="both", expand=True)

    formFrame = ttk.Frame(mainFrame, padding=10)
    formFrame.pack(side="left", fill="both", expand=True)

    treeFrame = ttk.Frame(mainFrame, padding=10)
    treeFrame.pack(side="right", fill="both", expand=True)

    # Form Fields
    promoCodeVar = tk.StringVar()
    descriptionVar = tk.StringVar()
    startDateVar = tk.StringVar()
    endDateVar = tk.StringVar()
    discountTypeVar = tk.IntVar(value=0)
    discountValueVar = tk.StringVar()
    discountLevelVar = tk.IntVar(value=0)
    selectedInventoryID = tk.IntVar(value=0)
    selectedItemName = tk.StringVar(value="None")

    ttk.Label(formFrame, text="Promo Code Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    promoEntry = ttk.Entry(formFrame, textvariable=promoCodeVar, width=25)
    promoEntry.grid(row=0, column=1, pady=5)

    ttk.Label(formFrame, text="Description:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    descEntry = ttk.Entry(formFrame, textvariable=descriptionVar, width=40)
    descEntry.grid(row=1, column=1, pady=5)

    ttk.Label(formFrame, text="Start Date (MM/DD/YYYY):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    startEntry = ttk.Entry(formFrame, textvariable=startDateVar, width=15)
    startEntry.grid(row=2, column=1, sticky="w", pady=5)

    ttk.Label(formFrame, text="End Date (MM/DD/YYYY):").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    endEntry = ttk.Entry(formFrame, textvariable=endDateVar, width=15)
    endEntry.grid(row=3, column=1, sticky="w", pady=5)

    ttk.Label(formFrame, text="Discount Type:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
    typeFrame = ttk.Frame(formFrame)
    typeFrame.grid(row=4, column=1, sticky="w")
    ttk.Radiobutton(typeFrame, text="Percent", variable=discountTypeVar, value=0).pack(side="left")
    ttk.Radiobutton(typeFrame, text="Dollar Amount", variable=discountTypeVar, value=1).pack(side="left")

    ttk.Label(formFrame, text="Discount Value:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
    valueEntry = ttk.Entry(formFrame, textvariable=discountValueVar, width=10)
    valueEntry.grid(row=5, column=1, sticky="w", pady=5)

    ttk.Label(formFrame, text="Discount Level:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
    levelFrame = ttk.Frame(formFrame)
    levelFrame.grid(row=6, column=1, sticky="w")
    ttk.Radiobutton(levelFrame, text="Cart Level", variable=discountLevelVar, value=0, command=lambda: toggleItemSearch()).pack(side="left")
    ttk.Radiobutton(levelFrame, text="Item Level", variable=discountLevelVar, value=1, command=lambda: toggleItemSearch()).pack(side="left")

    # Promo Codes Table
    promoTree = ttk.Treeview(treeFrame, columns=("Code", "Description", "Type", "Value", "Level", "Item", "Start", "End"), show="headings")
    for col in promoTree["columns"]:
        promoTree.heading(col, text=col)
        promoTree.column(col, width=50)
    promoTree.pack(fill="both", expand=True)

    searchFrame = ttk.Frame(window, padding=10)
    searchVar = tk.StringVar()

    searchEntry = ttk.Entry(searchFrame, textvariable=searchVar, width=30)
    searchButton = ttk.Button(searchFrame, text="Search", command=lambda: searchItems())
    itemTree = ttk.Treeview(searchFrame, columns=("Item Name", "Price"), show="headings", height=5)
    for col in itemTree["columns"]:
        itemTree.heading(col, text=col)

    searchEntry.grid(row=0, column=0, padx=5, pady=5)
    searchButton.grid(row=0, column=1, padx=5, pady=5)
    itemTree.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
    selectedItemLabel = ttk.Label(searchFrame, textvariable=selectedItemName)
    selectedItemLabel.grid(row=2, column=0, columnspan=2, pady=5)

    itemTree.bind("<ButtonRelease-1>", lambda event: selectItem())

    buttonFrame = tk.Frame(window, background="#7393B3")
    buttonFrame.pack(pady=20)

    ttk.Button(buttonFrame, text="Back", command=lambda: back()).pack(side="left", padx=5)
    ttk.Button(buttonFrame, text="Clear Fields", command=lambda: clearFields()).pack(side="left", padx=5)
    ttk.Button(buttonFrame, text="Delete Promo", command=lambda: deletePromo()).pack(side="left", padx=5)
    ttk.Button(buttonFrame, text="Add Promo", command=lambda: addPromo()).pack(side="left", padx=5)

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("PromoCodes"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")

    def toggleItemSearch():
        """
        Shows or hides the item search section depending on whether the discount
        level is set to 'Item Level' or not.
        """
        if discountLevelVar.get() == 1:
            searchFrame.pack()
        else:
            searchFrame.pack_forget()
            selectedInventoryID.set(0)
            selectedItemName.set("None")

    def searchItems():
        """
        Searches inventory items based on the entered keyword and populates the itemTree with results.
        """
        keyword = searchVar.get().strip()
        results = db.searchInventoryManager(keyword)
        itemTree.delete(*itemTree.get_children())
        for item in results:
            itemTree.insert("", "end", iid=item['InventoryID'], values=(item['ItemName'], f"${item['RetailPrice']:.2f}"))

    def selectItem():
        """
        Sets the selected inventory item from the search results into the selectedInventoryID and
        updates the UI label.
        """
        selected = itemTree.focus()
        if selected:
            selectedInventoryID.set(int(selected))
            selectedItemName.set(itemTree.item(selected)['values'][0])

    def clearFields():
        """
        Resets all input fields on the form and hides the item search section.
        """
        promoCodeVar.set("")
        descriptionVar.set("")
        startDateVar.set("")
        endDateVar.set("")
        discountTypeVar.set(0)
        discountValueVar.set("")
        discountLevelVar.set(0)
        selectedInventoryID.set(0)
        selectedItemName.set("None")
        toggleItemSearch()

    def back():
        """
        Clears the current screen and navigates back to the manager main page.
        """
        h.clearScreen(window)
        Manager.managerPage(window, personID)

    def loadPromos():
        """
        Loads all existing promo codes from the database and displays them in the promoTree view.
        """
        promoTree.delete(*promoTree.get_children())
        promos = db.getAllPromos()
        for promo in promos:
            typeText = "%" if promo['DiscountType'] == 0 else "$"
            levelText = "Cart" if promo['DiscountLevel'] == 0 else "Item"
            itemText = promo['ItemName'] if promo['ItemName'] else "-"
            value = f"{promo['DiscountPercentage']:.2f}" if promo['DiscountType'] == 0 else f"{promo['DiscountDollarAmount']:.2f}"
            promoTree.insert("", "end", iid=promo['DiscountID'],
                             values=(promo['DiscountCode'], promo['Description'], typeText,
                                     value, levelText, itemText, promo['StartDate'], promo['ExpirationDate']))

    def addPromo():
        """
        Validates input fields and attempts to insert a new promo code into the database.
        Provides success or error feedback via message boxes.
        """
        if not promoCodeVar.get().strip():
            messagebox.showerror("Error", "Promo Code Name is required.")
            return
        try:
            db.insertPromoCode(
                promoCodeVar.get(), descriptionVar.get(), discountLevelVar.get(),
                selectedInventoryID.get() if discountLevelVar.get() == 1 else None,
                discountTypeVar.get(), discountValueVar.get(),
                startDateVar.get(), endDateVar.get()
            )
            messagebox.showinfo("Success", "Promo code added.")
            loadPromos()
            clearFields()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def deletePromo():
        """
        Deletes the selected promo code from the database after confirmation.
        Displays message boxes for errors or confirmation.
        """
        selected = promoTree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a promo code to delete.")
            return
        try:
            db.deletePromoCode(int(selected))
            messagebox.showinfo("Success", "Promo code deleted.")
            loadPromos()
            clearFields()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    loadPromos()
    toggleItemSearch()
