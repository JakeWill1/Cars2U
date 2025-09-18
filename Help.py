import tkinter as tk
from tkinter import ttk
import sys
import os
from tkinter import PhotoImage

def helpPage(sourcePage):
    """
    Opens a new help window that provides context-specific instructions 
    based on the current page of the application.

    Args:
        sourcePage (str): The name of the page requesting help.
                          This determines which help instructions are displayed.

    Behavior:
        - Opens a new Tkinter Toplevel window centered on the screen.
        - Displays a title and help content relevant to the sourcePage.
        - Populates help tips from a predefined dictionary (HELPINFO).
        - Provides a Close button to exit the help window.
    """

    # Create a new window
    helpWindow = tk.Toplevel()
    helpWindow.title(f"Help - {sourcePage}")
    helpWindow.configure(background="#7393B3")
    helpWidth = 1000
    helpHeight = 650

    def resourcePath(relativePath):
        """
        Returns the absolute path to a resource.

        Args:
            relativePath (str): The relative path to the resource.

        Returns:
            str: The full path to the resource file.
        """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relativePath)

    iconPath = resourcePath("Images/Logo.png")

    try:
        icon = PhotoImage(file=iconPath)
        helpWindow.iconphoto(False, icon)
    except Exception as e:
        print(f"Error loading icon: {e}")

    # Screen dimensions
    screenWidth = helpWindow.winfo_screenwidth()
    screenHeight = helpWindow.winfo_screenheight()

    # Calculate center position
    xPos = (screenWidth // 2) - (helpWidth // 2) + 20
    yPos = (screenHeight // 2) - (helpHeight // 2) - 20

    # Set window geometry
    helpWindow.geometry(f"{helpWidth}x{helpHeight}+{xPos}+{yPos}")

    titleLabel = tk.Label(helpWindow, text=f"How to Use the {sourcePage} Page", bg="#7393B3", font=("Calibri", 18, "bold"))
    titleLabel.pack(pady=15)

    contentFrame = tk.Frame(helpWindow, bg="#7393B3")
    contentFrame.place(relx=.52, rely=.4, anchor="center")

    # Dictionary (page - instructions)
    HELPINFO = {
        "Customer": [
            "Browse the list of available vehicles.",
            "Click a vehicle image to see more details.",
            "Type vehicle name in top box or select a category from the dropdown menu and click 'Search' to filter.",
            "Click the 'Previous' or 'Next' buttons to navigate pages.",
            "To browse all vehicles after using a filter - ensure the search box is empty, the category is set to 'All', and click 'Search'"],

        "Product": [
            "View the full vehicle details.",
            "Select a package from the dropdown.",
            "Click 'Add to Cart' to add it.",
            "Click 'Back' to return to the Customer page."],

        "Cart": [
            "Review items in your cart.",
            "Change quantities or remove items (Item must be selected first by clicking on it).",
            "Apply a promo code for a discount (One promo code per order).",
            "Click 'Proceed' to enter card details."],

        "Register": [
            "Fill in all required personal information (Marked with an asterisk *).",
            "Create a unique username and secure password.",
            "Choose and answer 3 security questions.",
            "Click 'Submit' to complete registration."],

        "Login": [
            "Enter your username and password to log in.",
            "Click 'Register' to create a new account.",
            "Click 'Forgot Password' to recover access (Must enter username before clicking button).",
            "Use 'Guest' to browse without logging in."],

        "Payment": [
            "Enter your credit card number (####-####-####-####).",
            "Enter the expiration date (MM/YY or MM/YYYY).",
            "Enter the 3-digit CCV.",
            "Click 'Complete Purchase' to finish the order."],

        "Forgot Password": [
            "Answer the three security questions.",
            "Create new password and confirm.",
            "Click 'Submit' to reset password."],

        "Manager": [
            "Update Inventory - Access inventory management tools.",
            "Inventory Restock - Update or restock inventory as needed. (Any inventory below the restock threshold will trigger a notification when loading into the manager page)",
            "Manage Accounts - Disable, add or update any and all accounts",
            "Add Promo Codes - Manage discounts and promo codes.",
            "View/Print Reports - Generate HTML reports for orders and inventory.",
            "Point of Sale - Perform purchases on behalf of a customer; Look up order history of a customer"],

        "UpdateInventory": [
            "Search inventory items by name.",
            "View current quantity, restock threshold, and other details.",
            "Add/Update product - Add a new product or search and select an existing product to update it.",
            "Delete inventory items that are no longer available.",
            "Update Quantity - Add X more items to inventory."],

        "AddInventory": [
            "Enter all details of new item.",
            "Enter any new package names and descriptions - click 'Add Package'",
            "Select a package from the list and click 'Remove Package' to delete it",
            "Browse computer for picture of item.",
            "If updating an item, all information will be auto filled and editable.",
            "If creating a new category for the product, the dropdown must be set to 'All'."],

        "RestockPage": [
            "Show all items that are below the restock threshold.",
            "Refresh - Update the list."],

        "ManageAccounts": [
            "Can select an account from the list.",
            "Disable Account - Disables selected account",
            "Add/Update Account - Add acount if none selected; Update an account if selected from list."],

        "RegisterManager": [
            "Fill in all required personal information (Marked with an asterisk *).",
            "Create a unique username and secure password.",
            "Choose and answer 3 security questions.",
            "Click 'Submit' to complete registration.",
            "Dropdown menu will select if this is a customer account or a manager account."],

        "PromoCodes": [
            "View existing promo codes in the list.",
            "Fill out the form to create a new promo code (Name, Description, Start/End Date, Discount Type and Value, Level).",
            "If 'Percent' is selected, enter percentage as a decimal (10% would be 0.1).",
            "If 'Item Level' is selected, search and select the applicable item.",
            "Click 'Add Promo' to save a new promo code.",
            "Click 'Delete Promo' to remove an existing promo code.",
            "Click 'Clear Fields' to reset the form."],

        "Reports": [
            "Select 'Sales Reports' tab or 'Inventory Reports' tab.",
            "Select desired option and click 'Generate Sales Report'.",],

        "CustomerLookup": [
            "Select an option from the dropdown to search by.",
            "Type in search information into the box.",
            "Click 'Search'.",
            "Selecting a customer from the list and clicking 'Customer Orders' will provide a list of order history."
            "Selecting a customer from the list and clicking 'Select Customer' will take you through normal purchasing pages."],

        "CartManager": [
            "Review items in your cart.",
            "Change quantities or remove items (Item must be selected first by clicking on it).",
            "List of all applicable promo codes are available to view, select, and apply to order (One per order).",
            "Click 'Proceed' to enter card details."],

        "Favorite": [
            "Review favorited vehicles.",
            "Change order by setting new value in 'Order' box and pressing 'Enter' or 'Save Sort Order'.",
            "Click a vehicle image to see more details.",
            "Click 'Remove' to delete a vehicle from your favorites."]}
    
    # Entry based on current page
    helpItems = HELPINFO[sourcePage]

    # Iterate through entry and place on screen
    for tip, definition in enumerate(helpItems, start=1):
        label = tk.Label(contentFrame, text=f"{tip}. {definition}", wraplength=540, bg="#7393B3", font=("Calibri", 18, "bold"))
        label.pack(anchor="w", pady=5)

    # Close button
    closeButton = ttk.Button(helpWindow, text="Close", command=helpWindow.destroy)
    closeButton.place(relx=.45, rely=.7)