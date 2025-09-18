import tkinter as tk
from tkinter import ttk
import Helper as h
import Login
import Help
import DBLibrary as db
import Product
import Cart
import Manager
import Favorite

searchState = {"keyword": "",
               "category": ""}

def customerPage(window, personID, pageNumber, managerID=None):
    """
    Displays the Customer Page interface.

    This page allows users (or guests) to:
    - Browse products with pagination
    - Filter products by keyword or category
    - Click a product to view details
    - Navigate to Cart or Favorites pages
    - Return to the login or manager page depending on session
    - Access Help

    Args:
        window (tk.Tk): The main application window.
        personID (int or None): Logged-in user's PersonID, or None for guest access.
        pageNumber (int): The current page number for pagination.
        managerID (int or None): If in manager-assisted POS mode, the manager's PersonID.
    """
    ITEMS_PER_PAGE = 12
    keyword = searchState["keyword"]
    category = searchState["category"]

    if keyword or (category and category != "All"):
        totalItems = db.countSearchInventory(keyword, category)
    else:
        totalItems = db.getInventoryCount()
    maxPage = (totalItems -1) // ITEMS_PER_PAGE

    def back():
        """
        Navigates back to the Login page or Manager page depending on session type.
        Clears the screen and inventory cache.
        """
        h.clearScreen(window)
        h.clearInventoryCache()
        if managerID:
            Manager.managerPage(window, managerID)
        else:
            Login.loginPage(window)

    def cart():
        """
        Navigates to the Cart page for the current user.
        """
        h.clearScreen(window)
        Cart.cartPage(window, personID, pageNumber, managerID)

    def previous():
        """
        Navigates to the previous page of products if available.
        """
        if pageNumber > 0:
            h.clearScreen(window)
            customerPage(window, personID, pageNumber - 1)

    def next():
        """
        Navigates to the next page of products if available.
        """
        if pageNumber < maxPage:
            h.clearScreen(window)
            customerPage(window, personID, pageNumber + 1)

    def fav():
        """
        Navigates to the Favorites page for the current user.
        """
        h.clearScreen(window)
        Favorite.favoritePage(window, personID, pageNumber, managerID)

    window.configure(background="#7393B3")
    
    # filter contents (search item or category)
    filterFrame = tk.Frame(window, bg="#7393B3")
    filterFrame.pack(pady=5)

    searchEntry = ttk.Entry(filterFrame, width=50)
    searchEntry.pack(side="left", padx=5)

    categoryVar = tk.StringVar()
    categories = db.getCategories()
    categoryDropdown = ttk.OptionMenu(filterFrame, categoryVar, categories[0], *categories)
    categoryDropdown.pack(side="left", padx=5)

    def refreshProductDisplay(items):
        """
        Populates the product display grid with items.

        Args:
            items (list): A list of product dictionaries to display.
        """
        for widget in productFrame.winfo_children():
            widget.destroy()

        columns = 4
        imgSize = (150, 100)

        for index, item in enumerate(items):
            row = index // columns
            col = index % columns

            frame = ttk.Frame(productFrame, relief="raised", padding=5)
            frame.grid(row=row, column=col, padx=10, pady=10)

            image = h.convertToTkImage(item['ItemImage'], item['InventoryID'], imgSize)
            imgLabel = tk.Label(frame, image=image, cursor="hand2")
            imgLabel.image = image
            imgLabel.pack()

            nameLabel = ttk.Label(frame, text=item['ItemName'], font=("Calibri", 10))
            nameLabel.pack(pady=5)

            imgLabel.bind("<Button-1>", lambda e, it=item: product(it))

    def searchProducts():
        """
        Performs a product search using the provided keyword and category.
        Resets to the first page of results.
        """
        searchState["keyword"] = searchEntry.get().strip()
        searchState["category"] = categoryVar.get()
        h.clearScreen(window)
        customerPage(window, personID, 0, managerID)

    searchButton = ttk.Button(filterFrame, text="Search", command=searchProducts)
    searchButton.pack(side="left", padx=5)

    productFrame = tk.Frame(window, bg="#7393B3")
    productFrame.pack(pady=10)

    # Get items from DB and store the rendered pages for faster loading
    cacheKey = (pageNumber, keyword.lower(), category.lower())

    if cacheKey in h.pageCache:
        items = h.pageCache[cacheKey]
    else:
        if keyword or (category and category != "All"):
            items = db.searchInventory(keyword, category, pageNumber * ITEMS_PER_PAGE, ITEMS_PER_PAGE)
        else:
            items = db.getPageInventory(pageNumber * ITEMS_PER_PAGE, ITEMS_PER_PAGE)
    h.pageCache[cacheKey] = items


    def product(item):
        """
        Navigates to the Product Details page for the selected item.

        Args:
            item (dict): The product dictionary containing item details.
        """
        h.clearScreen(window)
        Product.productPage(window, item, personID, pageNumber, False, managerID)

    refreshProductDisplay(items)

    # Page buttons
    pageFrame = tk.Frame(window, bg="#7393B3")
    pageFrame.place(relx=.4, rely=.85)
    prevButton = ttk.Button(pageFrame, text="Previous", command=previous)
    prevButton.pack(side="left", padx=10)
    nextButton = ttk.Button(pageFrame, text="Next", command=next)
    nextButton.pack(side="left", padx=10)
        
    # Bottom buttons
    buttonFrame = tk.Frame(window, background="#7393B3")
    buttonFrame.place(relx=.4, rely=.91)

    backButton = ttk.Button(buttonFrame, text="Back", command=back)
    backButton.pack(side="left", padx=10)
    favButton = ttk.Button(buttonFrame, text="View Favorites", command=fav)
    favButton.pack(side="left", padx=10)
    checkoutButton = ttk.Button(buttonFrame, text="View Cart", command=cart)
    checkoutButton.pack(side="left", padx=10)

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("Customer"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")

    # Can not purchase if guest
    if personID is None:
        checkoutButton.config(state="disabled")
        favButton.config(state="disabled")
    else:
        checkoutButton.config(state="normal")
        favButton.config(state="normal")