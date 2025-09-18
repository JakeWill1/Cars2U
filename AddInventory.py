import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import DBLibrary as db
import Helper as h
import UpdateInventory
import Help
import os


def addInventoryPage(window, personID, itemID=None):
    """
    Displays the Add/Update Inventory Page UI.

    Allows a manager to:
    - Add a new product with optional image and packages
    - Update an existing product's details
    - Create new categories or select from existing ones
    - Attach multiple packages to a product

    Args:
        window (tk.Tk): The main application window.
        personID (int): The ID of the currently logged-in manager.
        itemID (int, optional): The InventoryID of the item to edit. If None, a new item is added.
    """
    window.configure(background="#7393B3")

    titleLabel = ttk.Label(window, text="Add New Product", font=("Calibri", 32, "bold"), background="#7393B3")
    titleLabel.pack(pady=20)

    formFrame = ttk.Frame(window)
    formFrame.pack(pady=10)

    fields = [
        ("Item Name", tk.StringVar()),
        ("Item Description", tk.StringVar()),
        ("Cost", tk.StringVar()),
        ("Retail Price", tk.StringVar()),
        ("Quantity", tk.StringVar()),
        ("Restock Threshold", tk.StringVar()),
        ("New Category", tk.StringVar()),
    ]

    entries = {}

    for i, (labelText, var) in enumerate(fields):
        label = ttk.Label(formFrame, text=labelText)
        label.grid(row=i, column=0, pady=5, padx=5, sticky="e")
        entry = ttk.Entry(formFrame, textvariable=var, width=30)
        entry.grid(row=i, column=1, pady=5, padx=5, sticky="w")
        entries[labelText] = var

    # Category dropdown
    categories = db.getCategories()
    categoryVar = tk.StringVar()
    categoryDropdown = ttk.OptionMenu(formFrame, categoryVar, categories[0], *categories)
    categoryDropdown.grid(row=6, column=1, pady=5, padx=5, sticky="e")

    # Packages
    packageFrame = ttk.LabelFrame(window, text="Packages", padding=10)
    packageFrame.pack(pady=10)

    packageNameLabel = ttk.Label(packageFrame, text="Name")
    packageNameLabel.grid(row=0, column=0, padx=5, pady=5)
    packageDescriptionLabel = ttk.Label(packageFrame, text="Description")
    packageDescriptionLabel.grid(row=0, column=1, padx=5, pady=5)

    packageNameVar = tk.StringVar()
    packageDescVar = tk.StringVar()

    packageNameEntry = ttk.Entry(packageFrame, textvariable=packageNameVar, width=20)
    packageNameEntry.grid(row=1, column=0, padx=5, pady=5)
    packageDescEntry = ttk.Entry(packageFrame, textvariable=packageDescVar, width=40)
    packageDescEntry.grid(row=1, column=1, padx=5, pady=5)

    packageList = []
    packageListBox = tk.Listbox(packageFrame, height=5, width=60)
    packageListBox.grid(row=2, column=0, columnspan=2, pady=5)

    if itemID:
        productData = db.getItemByID(itemID)
        packages = db.getProductPackages(itemID)
        
        # Auto fill fields
        entries["Item Name"].set(productData["ItemName"])
        entries["Item Description"].set(productData["ItemDescription"])
        entries["Cost"].set(str(productData["Cost"]))
        entries["Retail Price"].set(str(productData["RetailPrice"]))
        entries["Quantity"].set(str(productData["Quantity"]))
        entries["Restock Threshold"].set(str(productData["RestockThreshold"]))

        # Set the category dropdown
        categoryVar.set(productData["CategoryName"])
    
        # Auto fill packages
        for pkg in packages:
            packageList.append({"name": pkg["name"], "description": pkg["description"]})
            packageListBox.insert("end", f"{pkg['name']} - {pkg['description']}")

    def back():
        """
        Returns to the Update Inventory page.
        """
        h.clearScreen(window)
        UpdateInventory.updateInventoryPage(window, personID)

    def addPackage():
        """
        Adds a package (name and description) to the package list and listbox display.
        """
        name = packageNameVar.get().strip()
        desc = packageDescVar.get().strip()
        if name and desc:
            packageList.append({"name": name, "description": desc})
            packageListBox.insert("end", f"{name} - {desc}")
            packageNameVar.set("")
            packageDescVar.set("")
        else:
            messagebox.showwarning("Missing Fields", "Please enter both a package name and description.")

    def removePackage():
        """
        Removes the selected package from the list and listbox.
        """
        selectedIndex = packageListBox.curselection()
        if not selectedIndex:
            messagebox.showwarning("No Selection", "Please select a package to remove.")
            return
    
        index = selectedIndex[0]
        packageListBox.delete(index)
        packageList.pop(index)

    addPackageButton = ttk.Button(packageFrame, text="Add Package", command=addPackage)
    addPackageButton.grid(row=1, column=2, padx=5, pady=5)
    removePackageButton = ttk.Button(packageFrame, text="Remove Package", command=removePackage)
    removePackageButton.grid(row=2, column=2, padx=5, pady=5)

    # Image
    imageFrame = ttk.Frame(window)
    imageFrame.pack(pady=10)

    imagePath = tk.StringVar()
    imageNameLabel = ttk.Label(imageFrame, text="No file selected")
    imageNameLabel.pack(side="left", padx=5)

    def browseImage():
        """
        Opens a file dialog to allow the user to select an image file.
        Sets the image path and updates the label display.
        """
        filePath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if filePath:
            imagePath.set(filePath)
            imageNameLabel.config(text=os.path.basename(filePath))

    imageButton = ttk.Button(imageFrame, text="Browse", command=browseImage)
    imageButton.pack(side="left", padx=5)


    def submit(new):
        """
        Submits the form for either creating or updating an inventory item.

        Args:
            new (bool): If True, adds a new item. If False, updates existing one.
        """
        try:
            name = entries["Item Name"].get().strip()
            desc = entries["Item Description"].get().strip()
            newCategory = entries["New Category"].get().strip()
            selectedCategory = categoryVar.get()
            cost = float(entries["Cost"].get().strip())
            price = float(entries["Retail Price"].get().strip())
            qty = int(entries["Quantity"].get().strip())
            threshold = int(entries["Restock Threshold"].get().strip())
            packages = packageList
            packagesCopy = packageList.copy()
            image = imagePath.get()

            if not name or not desc or not cost or not price or not qty or not threshold:
                raise ValueError("Missing required fields.")
            
            if newCategory and selectedCategory and selectedCategory != "All":
                messagebox.showerror("Category Error", "Please either enter a new category or select an existing one, not both.")
                return
            
            category = newCategory if newCategory else selectedCategory
            if not category or category == "All":
                messagebox.showerror("Category Error", "Please select or enter a valid category.")
                return
            imageBlob = None
            if new:
                if image:
                    imageBlob = h.convertImageToBlob(image)
                else:
                    raise ValueError("Missing image.")
                db.addInventoryItem(name, desc, category, cost, price, qty, threshold, packages, imageBlob)
                messagebox.showinfo("Success", f"'{name}' added successfully!")
            else:
                if image:
                    imageBlob = h.convertImageToBlob(image)
                db.updateInventoryItem(itemID, name, desc, category, cost, price, qty, threshold, packagesCopy, imageBlob)
                messagebox.showinfo("Success", f"'{name}' updated successfully!")
            back()

        except Exception as e:
            print(f"Error adding inventory: {e}")
            messagebox.showerror("Error", "Please ensure all fields are filled out correctly.")

    buttonFrame = tk.Frame(window, background="#7393B3")
    buttonFrame.pack(pady=15)

    backButton = ttk.Button(buttonFrame, text="Back", command=back)
    backButton.pack(side="left", padx=10)

    addButton = ttk.Button(buttonFrame, text="Add Product", command=lambda: submit(True))
    addButton.pack(side="left", padx=10)
    updateButton = ttk.Button(buttonFrame, text="Update Product", command=lambda: submit(False))
    updateButton.pack(side="left", padx=10)

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("AddInventory"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")

    if itemID:
        addButton.config(state=tk.DISABLED)
        updateButton.config(state=tk.NORMAL)
    else:
        addButton.config(state=tk.NORMAL)
        updateButton.config(state=tk.DISABLED)