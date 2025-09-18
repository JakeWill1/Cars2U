import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re
import datetime
from PIL import Image, ImageTk
import io
from pathlib import Path
import webbrowser
import DBLibrary as db
import os

def clearScreen(window):
    """
    Clears all widgets from the given Tkinter window.
    
    Args:
        window (tk.Tk): The window to clear.
    """
    for widget in window.winfo_children():
            widget.destroy()

def setFrame(frame, state):
    """
    Sets the state (enabled/disabled) for all Entry and Label widgets in a frame.

    Args:
        frame (tk.Frame): The frame containing widgets.
        state (str): The desired state (e.g., 'normal', 'disabled').
    """
    for child in frame.winfo_children():
        if isinstance(child, (ttk.Entry, ttk.Label)):
                child.config(state=state)

def clearAllInputs(frame):
    """
    Clears the content of all Entry widgets in the given frame.

    Args:
        frame (tk.Frame): The frame containing Entry widgets.
    """
    for child in frame.winfo_children():
        if isinstance(child, ttk.Entry):
                child.delete(0, tk.END)

def clearSingleInput(field):
    """
    Clears the content of a single Entry widget.

    Args:
        field (ttk.Entry): The entry widget to clear.
    """
    field.delete(0, tk.END)

def checkUsername(username, field1):
    """
    Validates a username against defined rules.

    Args:
        username (str): The entered username.
        field1 (ttk.Entry): The Entry widget to clear on error.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not (8 <= len(username) <= 20):
        clearSingleInput(field1)
        messagebox.showerror(title="Invalid Username", message="Username must be between 8 and 20 characters long.")
        return False
    if username[0].isdigit():
        clearSingleInput(field1)
        messagebox.showerror(title="Invalid Username", message="Username can not start with a number.")
        return False
    if username.strip() != username or " " in username:
        clearSingleInput(field1)
        messagebox.showerror(title="Invalid Username", message="Username cannot start with, end with, or contain spaces.")
        return False
    if not re.match(r"^[A-Za-z0-9]+$", username):
        clearSingleInput(field1)
        messagebox.showerror(title="Invalid Username", message="Username cannot contain special characters.")
        return False
      
    unique = db.userExists(field1.get())

    if unique:
        clearSingleInput(field1)
        messagebox.showerror(title="Invalid Username", message="Please choose a different username")
        return False
    return True

def checkPassword(password, confirmPassword, field1, field2):
    """
    Validates a password for strength and format.

    Args:
        password (str): The entered password.
        confirmPassword (str): Re-entered password for confirmation.
        field1 (ttk.Entry): Password entry widget.
        field2 (ttk.Entry): Confirm password entry widget.

    Returns:
        bool: True if valid, False otherwise.
    """
    if " " in password:
        clearSingleInput(field1)
        clearSingleInput(field2)
        messagebox.showerror(title="Invalid Password", message="Password can not contain spaces")
        return False
    hasUpper = bool(re.search(r"[A-Z]", password))
    hasLower = bool(re.search(r"[a-z]", password))
    hasDigit = bool(re.search(r"\d", password))
    hasSpecial = bool(re.search(r"[()!@#$%^&*]", password))

    if re.search(r"[^A-Za-z0-9()!@#$%^&*]", password):
        clearSingleInput(field1)
        clearSingleInput(field2)
        messagebox.showerror(title="Invalid Password", message="Password contains invalid characters. May only contain ()!@#$%^&*")
        return False

    count = sum([hasUpper, hasLower, hasDigit, hasSpecial])

    if not (8 <= len(password) <= 20):
        clearSingleInput(field1)
        clearSingleInput(field2)
        messagebox.showerror(title="Invalid Password", message="Password must be between 8 and 20 characters long.")
        return False
    if password != confirmPassword:
        clearSingleInput(field2)
        messagebox.showerror(title="Passwords do not match", message="Please enter matching password")
        return False
    if count >= 3:
        return True
    else:
        clearSingleInput(field1)
        clearSingleInput(field2)
        messagebox.showerror(title="Missing Requirements", message="Please review the password requirements")
        return False
      
def checkNames(name):
    """
    Validates a name to ensure it does not contain special characters.

    Args:
        name (str): The name string.

    Returns:
        bool: True if valid, False otherwise.
    """
    if re.search(r"[^A-Za-z0-9]", name):
        messagebox.showerror(title="Name Error", message="Names can not contain special characters")
        return False
    return True

def validateCard(cardNumber, cardExp, ccv):
    """
    Validates card number, expiration date, and CCV.

    Args:
        cardNumber (str): The credit card number (####-####-####-####).
        cardExp (str): Expiration date (MM/YYYY).
        ccv (str): 3-digit CCV.

    Returns:
        bool: True if all fields are valid, False otherwise.
    """
    cardPattern = r"^\d{4}-\d{4}-\d{4}-\d{4}$"
    if not re.match(cardPattern, cardNumber):
        messagebox.showerror("Card Error", "Card number must be in the format ####-####-####-####.")
        return False

    
    if not re.fullmatch(r"\d{3}", ccv):
        messagebox.showerror("Card Error", "CCV must be 3 digits.")
        return False

    
    try:
        expMonth, expYear = cardExp.split('/')
        expMonth = int(expMonth)
        expYear = int(expYear)

        if expYear < 100:
            expYear += 2000

        currentYear = datetime.datetime.now().year
        currentMonth = datetime.datetime.now().month

        if not (1 <= expMonth <= 12):
            raise ValueError("Invalid month")

        if expYear < currentYear or (expYear == currentYear and expMonth < currentMonth):
            messagebox.showerror("Card Error", "Card has expired.")
            return False
        if expYear > currentYear + 5:
            messagebox.showerror("Card Error", "Card expiration is too far in the future.")
            return False

    except Exception as e:
        messagebox.showerror("Card Error", "Invalid expiration format. Use MM/YYYY.")
        return False

    return True

imageCache = {}

def convertToTkImage(imageBlob, inventoryID, size=(150, 100)):
    """
    Converts a BLOB image to a Tkinter-compatible PhotoImage, with caching.

    Args:
        imageBlob (bytes): Image data from the database.
        inventoryID (int): Unique ID to cache image.
        size (tuple): Desired image size (width, height).

    Returns:
        ImageTk.PhotoImage: The resized image or a gray placeholder.
    """
    if inventoryID in imageCache:
        return imageCache[inventoryID]
      
    if not imageBlob:
        # Return a blank placeholder image if None
        placeholder = Image.new("RGB", size, color="gray")
        image = ImageTk.PhotoImage(placeholder)
        imageCache[inventoryID] = image
        return image

    try:
        image = Image.open(io.BytesIO(imageBlob))
        image = image.resize(size, Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        imageCache[inventoryID] = photo
        return photo
    except Exception as e:
        print(f"Image conversion error: {e}")
        placeholder = Image.new("RGB", size, color="gray")
        image = ImageTk.PhotoImage(placeholder)
        imageCache[inventoryID] = image
        return image
      
cart = []

def addToCart(item):
    """
    Adds an item to the global cart. If it already exists with the same package, increases quantity.

    Args:
        item (dict): The item to add with keys: InventoryID, package, quantity.
    """
    for product in cart:
        if product['InventoryID'] == item['InventoryID'] and product['package'] == item['package']:
            product['quantity'] += item.get('quantity', 1)
            return
    cart.append(item)

def removeFromCart(item):
    """
    Removes an item from the cart that matches the InventoryID and package.

    Args:
        item (dict): The item to remove.
    """
    for product in cart:
        if product['InventoryID'] == item['InventoryID'] and product['package'] == item['package']:
            cart.remove(product)
            break
        
# Store inventory data for faster rendering
pageCache = {}

def clearInventoryCache():
     pageCache.clear()

def processOrder(cart, discount, personID, ccNumber, expDate, ccv, managerID=None):
    """
    Processes an order by inserting into Orders and OrderDetails, updating inventory.

    Args:
        cart (list): List of cart item dicts.
        discount (dict or None): Applied discount object.
        personID (int): Customer's person ID.
        ccNumber (str): Credit card number.
        expDate (str): Expiration date.
        ccv (str): Security code.
        managerID (int, optional): Employee processing the order.

    Returns:
        int: Generated order ID.
    """
    discountID = discount['DiscountID'] if discount else None

    # insert into orders table
    orderID = db.insertOrder(personID, discountID, ccNumber, expDate, ccv, managerID)

    # insert into order details table and update inventory
    for item in cart:
        db.insertOrderDetail(orderID, inventoryID=item['InventoryID'], quantity=item['quantity'], discountID=discountID)
        db.updateInventoryQuantity(inventoryID=item['InventoryID'], quantityChange=-item['quantity'])
    return orderID

def generateReceipt(cart, discount, orderID):
    """
    Generates an HTML receipt and opens it in the default web browser.

    Args:
        cart (list): List of purchased items.
        discount (dict): Applied discount.
        orderID (int): Order ID of the transaction.
    """
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    discountAmt = 0
    discountText = ""
    discountLine = ""
    newSubtotalLine = ""

    if discount:
        # Cart level
        if discount['DiscountLevel'] == 0:
            if discount['DiscountType'] == 0:
                discountAmt = subtotal * discount['DiscountPercentage']
                discountText = f"{int(discount['DiscountPercentage'] * 100)}%"
            else:
                discountAmt = discount['DiscountDollarAmount']
                discountText = f"${discountAmt:.2f}"
        # Item level
        elif discount['DiscountLevel'] == 1:
            for item in cart:
                if item['InventoryID'] == discount['InventoryID']:
                    if discount['DiscountType'] == 0:
                        discountAmt += item['price'] * item['quantity'] * discount['DiscountPercentage']
                    else:
                        discountAmt += discount['DiscountDollarAmount'] * item['quantity']
            discountText = f"{discount['DiscountCode']} - ${discountAmt:.2f}"

        discountLine = f"<p><strong>Discount:</strong> {discountText} (${discountAmt:.2f})</p>"
        newSubtotalLine = f"<p><strong>New Subtotal:</strong> ${subtotal - discountAmt:.2f}</p>"

    discountSubtotal = subtotal - discountAmt
    tax = discountSubtotal * 0.0825
    total = discountSubtotal + tax

    receiptFolder = Path.home() / "Documents" / "Cars2U"
    receiptFolder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = receiptFolder / f"Receipt_Order_{orderID}_{timestamp}.html"

    managerName = db.getManagerNameByOrder(orderID)

    with open(filename, "w") as f:
        f.write(f"""<!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <title>Cars2U Receipt</title>
            <style>
                  body {{
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 30px auto;
                        padding: 20px;
                        background-color: #f9f9f9;
                        border: 1px solid #ccc;
                        border-radius: 10px;
                  }}
                  h2 {{
                        text-align: center;
                        color: #333;
                  }}
                  table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 20px;
                  }}
                  th, td {{
                        border: 1px solid #ddd;
                        padding: 10px;
                        text-align: center;
                  }}
                  th {{
                        background-color: #e0e0e0;
                  }}
                  p {{
                        font-size: 16px;
                  }}
                  .total {{
                        font-weight: bold;
                  }}
            </style>
            </head>
            <body>
            <h2>Cars2U Purchase Receipt</h2>
            <p><strong>Processed By:</strong> {managerName}</p>
            <table>
                  <tr>
                        <th>Product Name</th>
                        <th>Item Price</th>
                        <th>Quantity</th>
                        <th>Line Total</th>
                  </tr>
            """)

        for item in cart:
            line_total = item['price'] * item['quantity']
            f.write(f"""<tr>
                  <td>{item['name']}</td>
                  <td>${item['price']:.2f}</td>
                  <td>{item['quantity']}</td>
                  <td>${line_total:.2f}</td>
                  </tr>""")

        f.write(f"""</table>
            <p><strong>Subtotal:</strong> ${subtotal:.2f}</p>
            {discountLine}
            {newSubtotalLine}
            <p><strong>Tax (8.25%):</strong> ${tax:.2f}</p>
            <p class="total"><strong>Total:</strong> ${total:.2f}</p>
            <p style="text-align: center;">Thank you for shopping with Cars2U!</p>
            </body>
            </html>""")

    webbrowser.open(str(filename))

def convertImageToBlob(filepath):
    """
    Converts an image file to binary BLOB format for DB storage.

    Args:
        filepath (str): Path to image file.

    Returns:
        bytes or None: Image binary data or None if error occurs.
    """
    try:
        with open(filepath, "rb") as file:
                blobData = file.read()
        return blobData
    except Exception as e:
        print(f"Error converting image to blob: {e}")
        return None
      
def generateDailySalesReport(dateObj):
    """
    Generates an HTML sales report for a specific day.

    Args:
        dateObj (datetime.date): Target date.
    """
    sales = db.getSalesByDate(dateObj)
    generateSalesHTMLReport(sales, f"Daily Sales Report - {dateObj.strftime('%m-%d-%Y')}")

def generateWeeklySalesReport(startDate):
    """
    Generates an HTML sales report for a specific week.

    Args:
        startDate (datetime.date): Starting date of the week.
    """
    sales = db.getSalesByWeek(startDate)
    generateSalesHTMLReport(sales, f"Weekly Sales Report Starting {startDate.strftime('%m-%d-%Y')}")

def generateMonthlySalesReport(month, year):
    """
    Generates an HTML sales report for a specific month.

    Args:
        month (int): Month (1-12).
        year (int): Year (4-digit).
    """
    sales = db.getSalesByMonth(month, year)
    generateSalesHTMLReport(sales, f"Monthly Sales Report - {month:02d}/{year}")

def generateInventoryReportForSale():
    """
    Generates an HTML report for all items available for sale.
    """
    items = db.getInventoryForSale()
    generateInventoryHTMLReport(items, "Inventory - Items For Sale")

def generateInventoryReportRestock():
    """
    Generates an HTML report for items needing restock.
    """
    items = db.getInventoryRestock()
    generateInventoryHTMLReport(items, "Inventory - Items Needing Restock")

def generateInventoryReportAll():
    """
    Generates an HTML report for all items including discontinued.
    """
    items = db.getAllInventoryIncludingDiscontinued()
    generateInventoryHTMLReport(items, "Inventory - All Items")

def generateSalesHTMLReport(sales, title):
    """
    Writes a sales report in HTML format and opens it.

    Args:
        sales (list): List of sales records.
        title (str): Title for the report.
    """
    if not sales:
        messagebox.showinfo("No Sales Found", "No sales records found for the selected period.")
        return
    
    documents = Path.home() / "Documents" / "Cars2UReports"
    documents.mkdir(parents=True, exist_ok=True)

    filename = documents / f"{title.replace(' ', '_').replace('/', '-')}.html"

    with open(filename, "w") as f:
        f.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid black; padding: 8px; text-align: center; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
        <h2>{title}</h2>
        <table>
            <tr>
                <th>Order ID</th>
                <th>Date</th>
                <th>Subtotal</th>
                <th>Tax</th>
                <th>Total</th>
            </tr>
        """)
        for order in sales:
            f.write(f"<tr><td>{order['OrderID']}</td><td>{order['OrderDate']}</td><td>${order['Subtotal']:.2f}</td><td>${order['Tax']:.2f}</td><td>${order['Total']:.2f}</td></tr>")

        f.write("""
        </table>
        </body>
        </html>
        """)
    os.startfile(filename)

def generateInventoryHTMLReport(items, title):
    """
    Writes an inventory report in HTML format and opens it.

    Args:
        items (list): List of inventory items.
        title (str): Title for the report.
    """
    if not items:
        messagebox.showinfo("No Items Found", "No inventory records found matching the selected criteria.")
        return
    
    documents = Path.home() / "Documents" / "Cars2UReports"
    documents.mkdir(parents=True, exist_ok=True)

    filename = documents / f"{title.replace(' ', '_')}.html"

    with open(filename, "w") as f:
        f.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid black; padding: 8px; text-align: center; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
        <h2>{title}</h2>
        <table>
            <tr>
                <th>Inventory ID</th>
                <th>Item Name</th>
                <th>Cost</th>
                <th>Retail Price</th>
                <th>Quantity</th>
                <th>Restock Threshold</th>
                <th>Availability</th>
            </tr>
        """)
        for item in items:
            status = "Available" if item['Discontinued'] == 0 else "Discontinued"
            f.write(f"<tr><td>{item['InventoryID']}</td><td>{item['ItemName']}</td><td>${item['Cost']:.2f}</td><td>${item['RetailPrice']:.2f}</td><td>{item['Quantity']}</td><td>{item['RestockThreshold']}</td><td>{status}</td></tr>")

        f.write("""
        </table>
        </body>
        </html>
        """)
    os.startfile(filename)