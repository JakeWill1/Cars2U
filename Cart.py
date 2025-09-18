import tkinter as tk
from tkinter import ttk, messagebox
import Helper as h
import Customer
import Payment
import DBLibrary as db
import Help

discount = None
totalLabel = None

def cartPage(window, personID, pageNumber, managerID=None):
    """
    Displays the Cart Page UI where the user can view and manage cart items.

    Functionality includes:
    - Modifying quantity of items
    - Removing or clearing items
    - Viewing subtotal, discounts, tax, and final total
    - Applying promotional codes
    - Proceeding to the payment page
    - Viewing manager-only available discounts (if POS mode)

    Args:
        window (tk.Tk): The root application window.
        personID (int): The ID of the currently logged-in customer.
        pageNumber (int): The page number to return to in the customer view.
        managerID (int, optional): The ID of the logged-in manager for POS mode. Defaults to None.
    """
    window.configure(background="#7393B3")

    title = ttk.Label(window, text="Your Cart", font=("Calibri", 28, "bold"), background="#7393B3")
    title.pack(pady=10)

    # Table form to display cart items
    tree = ttk.Treeview(window, columns=("Item", "Package", "Price", "Quantity", "Total"), show="headings", height=4)
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(pady=10)

    def refreshTree():
        """
        Refreshes the cart item tree view with current cart contents and updates total.
        """
        for row in tree.get_children():
            tree.delete(row)
        for i, entry in enumerate(h.cart):
            subtotal = entry['price'] * entry['quantity']
            tree.insert("", "end", iid=i, values=(entry['name'], entry['package'], f"${entry['price']:.2f}", entry['quantity'], f"${subtotal:.2f}"))
        updateTotal()
        
    def modifyQuantity():
        """
        Updates the quantity of the selected cart item after validating input and availability.
        """
        selected = tree.focus()
        if not selected:
            return
        try:
            qty = int(quantityVar.get())
            if qty <= 0:
                raise ValueError

            selectedIndex = int(selected)
            item = h.cart[selectedIndex]
            availableQty = db.checkQuantity(item['InventoryID'])

            if qty > availableQty:
                messagebox.showerror("Quantity Error", f"Only {availableQty} of '{item['name']}' are available.")
                item['quantity'] = availableQty
            else:
                item['quantity'] = qty

            refreshTree()
            quantityVar.set("")
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Please enter a valid quantity greater than 0.")


    def removeItem():
        """
        Removes the selected item from the cart.
        Disables checkout if the cart becomes empty.
        """
        selected = tree.focus()
        if selected:
            h.cart.pop(int(selected))
            refreshTree()
        if h.cart:
            proceedButton.config(state="normal")
        else:
            proceedButton.config(state="disabled")

    def clearCart():
        """
        Clears all items from the cart and disables the checkout button.
        """
        h.cart.clear()
        refreshTree()
        proceedButton.config(state="disabled")

    def applyPromo():
        """
        Validates and applies a promo code from the entry field to the current cart.
        Updates the total if successful.
        """
        global discount
        code = promoVar.get().strip()
        if not code:
            return
        result = db.validatePromoCode(code, h.cart)
        if result:
            discount = result
            messagebox.showinfo("Promo Applied", f"{code} applied successfully!")
        else:
            discount = None
            promoVar.set("")
            messagebox.showerror("Invalid Promo", "Promo code is not valid or does not match your cart items.")
        updateTotal()

    def updateTotal():
        """
        Recalculates the subtotal, discount, tax, and final total, and updates the display.
        """
        subtotal = float(sum(item['price'] * item['quantity'] for item in h.cart))
        discountText = ""
        discountAmt = 0

        if discount:
            if discount['DiscountLevel'] == 0:
                # Cart level Discount
                if discount['DiscountType'] == 0:
                    discountAmt = subtotal * discount['DiscountPercentage']
                    discountText = f"Cart Discount ({int(discount['DiscountPercentage']*100)}%): -${discountAmt:.2f}\n"
                elif discount['DiscountType'] == 1:
                    discountAmt = discount['DiscountDollarAmount']
                    discountText = f"Cart Discount: -${discountAmt:.2f}\n"

            elif discount['DiscountLevel'] == 1:
                # Item level Discount
                for item in h.cart:
                    if item['InventoryID'] == discount['InventoryID']:
                        if discount['DiscountType'] == 0:
                            discountAmt += item['price'] * item['quantity'] * discount['DiscountPercentage']
                        elif discount['DiscountType'] == 1:
                            discountAmt += discount['DiscountDollarAmount'] * item['quantity']
                if discountAmt > 0:
                    discountText = f"Item Discount ({discount['DiscountCode']}): -${discountAmt:.2f}\n"

        discountTotal = subtotal - discountAmt
        tax = discountTotal * 0.0825
        finalTotal = discountTotal + tax

        total_display = (
            f"Subtotal: ${subtotal:.2f}\n"
            f"{discountText}"
            f"Tax: +${tax:.2f}\n"
            f"Total: ${finalTotal:.2f}"
        )
        totalLabel.config(text=total_display)


    def back():
        """
        Navigates back to the customer product page.
        """
        h.clearScreen(window)
        Customer.customerPage(window, personID, pageNumber, managerID)

    def payment():
        """
        Proceeds to the payment page with the current cart and applied discount.
        """
        h.clearScreen(window)
        Payment.paymentPage(window, h.cart, discount, personID, pageNumber, managerID)

    # If manager using POS
    if managerID:
        discountFrame = ttk.Frame(window, padding=10)
        discountFrame.pack(pady=10)

        ttk.Label(discountFrame, text="Available Discounts:", font=("Calibri", 14, "bold")).pack()

        discountTree = ttk.Treeview(discountFrame, columns=("Code", "Type", "Amount", "Level", "ItemName"), show="headings", height=4)
        for col in discountTree["columns"]:
            discountTree.heading(col, text=col)
        discountTree.pack()

        def loadAvailableDiscounts():
            """
            Loads manager-available discounts from the database into the discount tree view.
            """
            discountTree.delete(*discountTree.get_children())
            availableDiscounts = db.getAvailableDiscounts(h.cart)
            for d in availableDiscounts:
                typeText = "%" if d['DiscountType'] == 0 else "$"
                levelText = "Cart" if d['DiscountLevel'] == 0 else "Item"
                itemText = d['ItemName'] if d['ItemName'] else "-"
                discountTree.insert("", "end", iid=d['DiscountID'],
                                    values=(d['DiscountCode'], typeText, d['DiscountAmount'], levelText, itemText))
                
        def applySelectedDiscount():
            """
            Applies the discount selected in the manager discount tree view.
            """
            selected = discountTree.focus()
            if not selected:
                messagebox.showerror("Error", "Select a discount to apply.")
                return
            code = discountTree.item(selected)["values"][0]
            global discount
            discount = db.validatePromoCode(code, h.cart)
            refreshTree()

        ttk.Button(discountFrame, text="Apply Selected Discount", command=applySelectedDiscount).pack(pady=5)


    # Quantity input
    quantityFrame = tk.Frame(window, background="#7393B3")
    quantityFrame.pack(pady=5)
    quantityVar = tk.StringVar()
    quantityLabel = ttk.Entry(quantityFrame, textvariable=quantityVar, width=5)
    quantityLabel.pack(side="left", padx=5)
    quantityButton = ttk.Button(quantityFrame, text="Update Quantity", command=modifyQuantity)
    quantityButton.pack(side="left", padx=5)
    removeButton = ttk.Button(quantityFrame, text="Remove Item", command=removeItem)
    removeButton.pack(side="left", padx=5)

    # Promo code input
    promoFrame = tk.Frame(window, background="#7393B3")
    promoFrame.pack(pady=5)
    promoVar = tk.StringVar()
    promoLabel = ttk.Entry(promoFrame, textvariable=promoVar, width=20)
    promoLabel.pack(side="left", padx=5)
    applyPromoButton = ttk.Button(promoFrame, text="Apply Promo", command=applyPromo)
    applyPromoButton.pack(side="left")

    # Total area
    global totalLabel
    totalLabel = ttk.Label(window, text="", background="#7393B3", font=("Arial", 14, "bold"))
    totalLabel.pack(pady=10)

    refreshTree()

    # Bottom buttons
    buttonFrame = tk.Frame(window, bg="#7393B3")
    buttonFrame.pack(pady=10)

    backButton = ttk.Button(buttonFrame, text="Back", command=back)
    backButton.pack(side="left", padx=10)
    clearButton = ttk.Button(buttonFrame, text="Clear Cart", command=clearCart)
    clearButton.pack(side="left", padx=10)
    proceedButton = ttk.Button(buttonFrame, text="Checkout", command=payment)
    proceedButton.pack(side="left", padx=10)
    
    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("Cart") if managerID is None else Help.helpPage("CartManager"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")

    if h.cart:
        proceedButton.config(state="normal")
    else:
        proceedButton.config(state="disabled")

    if managerID:
        loadAvailableDiscounts()
        h.clearScreen(promoFrame)