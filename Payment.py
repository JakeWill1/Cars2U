import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import Helper as h
import Customer
import Cart
import Help

def paymentPage(window, cart, discount, personID, pageNumber, managerID=None):
    """
    Displays the payment page where the user enters credit card information
    to complete the transaction.

    Args:
        window (tk.Tk or tk.Frame): The root window or frame for the GUI.
        cart (list): The user's cart containing selected product dictionaries.
        discount (dict or None): An optional discount applied to the order.
        personID (int): ID of the user placing the order.
        pageNumber (int): The page number the user was on in the cart.
        managerID (int, optional): If applicable, the ID of the employee processing the order.
    """
    window.configure(bg="#7393B3")

    def submit():
        """
        Validates user input for payment fields, processes the order if valid,
        and generates a receipt. Handles both input errors and backend failures.
        """
        card = cardVar.get().strip()
        exp = expVar.get().strip()
        ccv = ccvVar.get().strip()

        # Input Validation
        if not card or not exp or not ccv:
            messagebox.showerror("Error", "All fields are required.")
            return

        if not card.count("-") == 3 or not all(part.isdigit() and len(part) == 4 for part in card.split("-")):
            messagebox.showerror("Invalid Card", "Card number must be in format ####-####-####-####.")
            return

        if not (ccv.isdigit() and len(ccv) == 3):
            messagebox.showerror("Invalid CCV", "CCV must be 3 digits.")
            return

        try:
            if "/" not in exp:
                raise ValueError
            parts = exp.split("/")
            month = int(parts[0])
            year = int(parts[1]) + 2000 if len(parts[1]) == 2 else int(parts[1])
            if month < 1 or month > 12:
                raise ValueError
            expDate = datetime.date(year, month, 1)
            currentDate = datetime.date.today()
            maxYear = currentDate.year + 5
            if expDate < currentDate.replace(day=1) or year > maxYear:
                messagebox.showerror("Card Expired", "Card is expired or outside acceptable range.")
                return
        except:
            messagebox.showerror("Invalid Expiration", "Use format MM/YYYY or MM/YY.")
            return

        try:
            orderID = h.processOrder(cart, discount, personID, card, exp, ccv, managerID)
            h.generateReceipt(cart, discount, orderID)
        except Exception as e:
            messagebox.showerror("Order Failed", str(e))
            return
        h.cart.clear()
        messagebox.showinfo("Purchase Complete", "Transaction completed and receipt has been generated.")
        h.clearInventoryCache()
        h.cart.clear()
        returnCustomer()

    def back():
        """
        Returns the user to the Cart page with preserved context.
        """
        h.clearScreen(window)
        Cart.cartPage(window, personID, pageNumber, managerID)
    
    def returnCustomer():
        """
        Returns the user to the Customer page after a successful transaction.
        """
        h.clearScreen(window)
        Customer.customerPage(window, personID, 0, managerID)

    title = ttk.Label(window, text="Enter Payment Details", font=("Arial", 24, "bold"), background="#7393B3")
    title.place(relx=0.5, rely=0.2, anchor="center")

    # Main frame to center everything
    mainFrame = ttk.Frame(window, padding="30 30 30 30")
    mainFrame.place(relx=0.5, rely=0.4, anchor="center")

    form = ttk.Frame(mainFrame)
    form.pack()

    cardVar = tk.StringVar()
    expVar = tk.StringVar()
    ccvVar = tk.StringVar()

    # Card Number
    numberLabel = ttk.Label(form, text="Card Number (####-####-####-####)")
    numberLabel.grid(row=0, column=0, sticky="e", pady=5, padx=5)
    numberInput = ttk.Entry(form, textvariable=cardVar, width=25)
    numberInput.grid(row=0, column=1, pady=5, padx=5)

    # Expiration Date
    expLabel = ttk.Label(form, text="Expiration Date (MM/YYYY or MM/YY)")
    expLabel.grid(row=1, column=0, sticky="e", pady=5, padx=5)
    expInput = ttk.Entry(form, textvariable=expVar, width=15)
    expInput.grid(row=1, column=1, pady=5, padx=5)

    # Security Code
    codeLabel = ttk.Label(form, text="Security Code (CVV)")
    codeLabel.grid(row=2, column=0, sticky="e", pady=5, padx=5)
    codeInput = ttk.Entry(form, textvariable=ccvVar, width=5, show="*")
    codeInput.grid(row=2, column=1, pady=5, padx=5)

    # Bottom Buttons
    buttonFrame = tk.Frame(window, bg="#7393B3")
    buttonFrame.place(relx=0.39, rely=.6)

    backButton = ttk.Button(buttonFrame, text="Back", command=back)
    backButton.pack(side="left", padx=10)
    submitButton = ttk.Button(buttonFrame, text="Complete Purchase", command=submit)
    submitButton.pack(side="left", padx=10)

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("Payment"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")