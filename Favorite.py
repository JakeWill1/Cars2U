import tkinter as tk
from tkinter import ttk, PhotoImage
import DBLibrary as db
import Customer
import Product
import Helper as h
import Help
import sys
import os

def favoritePage(window, personID, pageNumber, managerID=None):
    """
    Displays the Favorite Vehicles page for a logged-in customer.

    Allows customers to:
        - View and navigate to product pages for their favorited items
        - Reorder items by setting a sort order
        - Add and edit notes for each favorite
        - Remove items from favorites
        - Navigate back or open a help window

    Args:
        window (tk.Tk or tk.Frame): The main application window or container.
        personID (int): The ID of the current customer.
        pageNumber (int): The previous page number for navigation purposes.
        managerID (int or None): Optional manager ID if called from a manager context.
    """
    window.configure(background="#7393B3")

    title = ttk.Label(window, text="Your Favorite Vehicles", font=("Calibri", 22, "bold"), background="#7393B3")
    title.pack(pady=10)

    def goToProduct(itemID):
        """
        Navigates to the product page of the selected favorite item.

        Args:
            itemID (int): The ID of the inventory item to open.
        """
        item = db.getItemByID(itemID)
        if item:
            h.clearScreen(window)
            Product.productPage(window, item, personID, pageNumber, True, managerID)

    def saveOrder():
        """
        Saves the current sort order of the favorite items to the database.
        """
        for i, fav in enumerate(favorites):
            db.updateSortOrder(fav[0], i + 1)
        refreshEntries()

    def remove(itemID):
        """
        Removes the selected item from the user's favorites.

        Args:
            itemID (int): The ID of the item to remove from favorites.
        """
        db.removeFavorite(personID, itemID)
        h.clearScreen(window)
        favoritePage(window, personID, pageNumber, managerID)

    # Scrollable canvas setup
    canvas = tk.Canvas(window, background="#7393B3", highlightthickness=0)
    frame = tk.Frame(canvas, background="#7393B3")
    scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=10)
    scrollbar.pack(side="right", fill="y")
    canvas.create_window((0, 0), window=frame, anchor="nw")

    def onMouseWheel(event):
        """
        Scrolls the canvas vertically when the mouse wheel is used.

        Args:
            event (tk.Event): The mouse wheel scroll event. The delta is used to
                            determine scroll direction and amount.
        """
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", onMouseWheel)

    def onFrameConfigure(event):
        """
        Updates the scrollable region of the canvas when the inner frame's size changes.

        Args:
            event (tk.Event): The configuration event triggered when the frame is resized.
        """
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame.bind("<Configure>", onFrameConfigure)

    def back():
        """
        Returns the user to the customer page from the favorites page.
        """
        h.clearScreen(window)
        Customer.customerPage(window, personID, pageNumber, managerID)

    def addNote(favoriteID):
        """
        Opens a pop-up window to add or update a note for the selected favorite.

        Args:
            favoriteID (int): The unique ID of the favorite entry.
        """
        noteWindow = tk.Toplevel()
        noteWindow.title("Notes")
        noteWindow.configure(background="#7393B3")
        noteWidth = 500
        noteHeight = 300

        # Add logo to window
        def resourcePath(relativePath):
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(base_path, relativePath)

        iconPath = resourcePath("Images/Logo.png")

        try:
            icon = PhotoImage(file=iconPath)
            noteWindow.iconphoto(False, icon)
        except Exception as e:
            print(f"Error loading icon: {e}")

        # Screen dimensions
        screenWidth = noteWindow.winfo_screenwidth()
        screenHeight = noteWindow.winfo_screenheight()

        # Calculate center position
        xPos = (screenWidth // 2) - (noteWidth // 2) + 20
        yPos = (screenHeight // 2) - (noteHeight // 2) - 20

        # Set window geometry
        noteWindow.geometry(f"{noteWidth}x{noteHeight}+{xPos}+{yPos}")

        currentNote = db.getNote(favoriteID)

        textBox = tk.Text(noteWindow, height=10, width=60, wrap="word")
        textBox.pack(pady=10, padx=20)
        textBox.insert("1.0", currentNote or "")

        def saveNote():
            newNote = textBox.get("1.0", "end-1c").strip()
            db.updateNote(favoriteID, newNote)
            for i in range(len(favorites)):
                if favorites[i][0] == favoriteID:
                    favorites[i] = (*favorites[i][:-1], newNote)
                    break
            noteWindow.destroy()
        saveButton = ttk.Button(noteWindow, text="Save", command=saveNote)
        saveButton.pack(pady=10)

    buttonFrame = tk.Frame(window, background="#7393B3")
    buttonFrame.place(relx=0.92, rely=0.4, anchor="n")

    saveButton = ttk.Button(buttonFrame, text="Save Sort Order", command=saveOrder)
    saveButton.pack(pady=5, fill="x")

    backButton = ttk.Button(buttonFrame, text="Back", command=lambda: back())
    backButton.pack(pady=5, fill="x")

    helpButton = ttk.Button(buttonFrame, text="Help", command=lambda: Help.helpPage("Favorite"))
    helpButton.pack(pady=5, fill="x")

    favorites = db.getFavorites(personID)

    if not favorites:
        ttk.Label(frame, text="You have no favorite products.", background="#7393B3", font=("Calibri", 14)).pack(pady=20)
        return
    
    entries = []
    sortVars = []
    columns = 4
    imgSize = (150, 100)

    def refreshEntries():
        """
        Refreshes the visual grid of favorite entries based on the current list.

        Handles image display, sort order input, note button, and remove button for each item.
        Also resets sort variables and entries list.
        """
        h.clearScreen(frame)
        sortVars.clear()
        entries.clear()

        for index, fav in enumerate(favorites):
            row = index // columns
            col = index % columns

            container = ttk.Frame(frame, relief="raised", padding=5)
            container.grid(row=row, column=col, padx=10, pady=10, sticky="n")

            image = h.convertToTkImage(fav[6], fav[2], size=imgSize)
            imgLabel = tk.Label(container, image=image, cursor="hand2")
            imgLabel.image = image
            imgLabel.pack()
            imgLabel.bind("<Button-1>", lambda e, it=fav[2]: goToProduct(it))
            nameLabel = ttk.Label(container, text=fav[3], font=("Calibri", 10))
            nameLabel.pack(pady=5)

            sortVar = tk.IntVar(value=index + 1)
            sortVars.append(sortVar)

            def onChange(event, index=index):
                """
                Triggered when a sort entry loses focus or Enter is pressed.
                Validates and applies new sort order, updating the list accordingly.

                Args:
                    event: The Tkinter event object.
                    index (int): The index of the item being changed.
                """
                try:
                    newSortVar = int(sortVars[index].get())
                    if newSortVar < 1 or newSortVar > len(favorites):
                        raise ValueError
                except ValueError:
                    tk.messagebox.showwarning("Invalid Input", "Sort order must be between 1 and number of items.")
                    sortVars[index].set(index + 1)
                    return
                item = favorites.pop(index)
                favorites.insert(newSortVar - 1, item)
                saveOrder()

            sortFrame = ttk.Frame(container)
            sortFrame.pack(pady=2)
            ttk.Label(sortFrame, text="Order:").pack(side="left")
            entry = ttk.Entry(sortFrame, width=3, textvariable=sortVar)
            entry.pack(side="left")
            entry.bind("<FocusOut>", onChange)
            entry.bind("<Return>", onChange)

            entries.append((fav[0], sortVar))

            noteButton = ttk.Button(container, text="Notes", command=lambda favID=fav[0], note=fav[7]: addNote(favID))
            noteButton.pack(pady=2)
            removeButton = ttk.Button(container, text="Remove", command=lambda itemID=fav[2]: remove(itemID))
            removeButton.pack(pady=2)

    refreshEntries()