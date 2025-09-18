import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import Helper as h
import Customer
import Help
import DBLibrary as db
import Favorite

def productPage(window, item, personID, pageNumber, isFavorite, managerID=None):
    """
    Displays the product detail page for a selected item. Allows users to view item details,
    choose a package, add to cart, and add to favorites.

    Args:
        window (tk.Tk or tk.Frame): The main application window.
        item (dict): Dictionary containing the product's data.
        personID (int or None): ID of the user viewing the product (None if not logged in).
        pageNumber (int): The page number to return to on back navigation.
        isFavorite (bool): Indicates whether the page was accessed from the Favorites page.
        managerID (int, optional): Manager ID if accessed in employee context.
    """
    window.configure(background="#7393B3")

    # Live update quantity
    updateItem = db.getItemByID(item["InventoryID"])
    if updateItem:
        item.update(updateItem)

    def back():
        """
        Navigates the user back to either the Favorites page or Customer page
        depending on where they came from.
        """
        h.clearScreen(window)
        if isFavorite:
            Favorite.favoritePage(window, personID, pageNumber, managerID=None)
        else:
            Customer.customerPage(window, personID, pageNumber, managerID)

    def addToCart():
        """
        Adds the current product with the selected package to the cart and returns
        the user to the Customer page.
        """
        selectedPackage = packageChoice.get() or "Standard"
        itemToAdd = {
            "InventoryID": item["InventoryID"],
            "name": item["ItemName"],
            "package": selectedPackage,
            "price": item["RetailPrice"],
            "quantity": 1
        }
        h.addToCart(itemToAdd)
        messagebox.showinfo("Cart", f"Added '{item['ItemName']}' with '{selectedPackage}' package to cart.")
        h.clearScreen(window)
        Customer.customerPage(window, personID, pageNumber, managerID)

    def fav():
        """
        Attempts to add the current product to the user's favorites.
        Shows a message box for success or duplicate warning.
        """
        added = db.addFavorite(personID, item["InventoryID"])
        if added:
            messagebox.showinfo("Success", "Added to favorites!")
        else:
            messagebox.showwarning("Duplicate", "Already in favorites.")
    
    # Title
    title = ttk.Label(window, text=item['ItemName'], font=("Calibri", 28, "bold"), background="#7393B3")
    title.pack(pady=10)

    # Product Image
    image = h.convertToTkImage(item['ItemImage'], item['InventoryID'], size=(300, 200))
    imgLabel = tk.Label(window, image=image, bg="#ffffff")
    imgLabel.image = image
    imgLabel.pack(pady=10)

    # Package dropdown
    packageFrame = ttk.Frame(window)
    packageFrame.pack(pady=5)
    packageLabel = ttk.Label(packageFrame, text="Packages:")
    packageLabel.pack(side="left", padx=5)
    packageChoice = tk.StringVar()
    packages = db.getProductPackages(item['InventoryID'])
    formattedPackages = [f"{pkg['name']} - {pkg['description']}" for pkg in packages]
    packageMenu = ttk.OptionMenu(packageFrame, packageChoice, formattedPackages[0], *formattedPackages)
    packageMenu.pack(side="left")

    # Product info
    infoFrame = tk.Frame(window, background="#7393B3")
    infoFrame.pack(pady=10)

    typeLabel = ttk.Label(infoFrame, text="Vehicle Type:", background="#7393B3", font=("Calibri", 12, "bold"))
    typeLabel.pack(anchor="w")
    typeInfoLabel = ttk.Label(infoFrame, text=f"{item['CategoryName']}", background="#7393B3", font=("Calibri", 12))
    typeInfoLabel.pack(anchor="w")
    descriptionLabel = ttk.Label(infoFrame, text=f"Description:", background="#7393B3", font=("Calibri", 12, "bold"))
    descriptionLabel.pack(anchor="w")
    descriptionInfoLabel = ttk.Label(infoFrame, text=item['ItemDescription'], background="#7393B3", font=("Calibri", 12), wraplength=600)
    descriptionInfoLabel.pack(anchor="w", pady=2)
    priceLabel = ttk.Label(infoFrame, text="Price: ", background="#7393B3", font=("Calibri", 12, "bold"))
    priceLabel.pack(anchor="w")
    priceInfoLabel = ttk.Label(infoFrame, text=f"${item['RetailPrice']:.2f}", background="#7393B3", font=("Calibri", 12))
    priceInfoLabel.pack(anchor="w")
    quantityLabel = ttk.Label(infoFrame, text="Quantity Available: ", background="#7393B3", font=("Calibri", 12, "bold"))
    quantityLabel.pack(anchor="w")
    quantityInfoLabel = ttk.Label(infoFrame, text=f"{item['Quantity']}", background="#7393B3", font=("Calibri", 12))
    quantityInfoLabel.pack(anchor="w")

    # Bottom buttons
    buttonframe = tk.Frame(window, bg="#7393B3")
    buttonframe.pack(pady=15)

    backButton = ttk.Button(buttonframe, text="Back", command=back)
    backButton.pack(side="left", padx=10)
    favButton = ttk.Button(buttonframe, text="Add To Favorites", command=fav)
    favButton.pack(side="left", padx=10)
    addcartButton = ttk.Button(buttonframe, text="Add to Cart", command=addToCart)
    addcartButton.pack(side="left", padx=10)

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("Product"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")

    if personID is None:
        addcartButton.config(state="disabled")
        favButton.config(state="disabled")
    else:
        addcartButton.config(state="normal")
        favButton.config(state="normal")

    if isFavorite: 
        favButton.config(state="disabled")
    else:
        favButton.config(state="normal")