import sqlite3
import os
from tkinter import messagebox
from datetime import date, datetime
from pathlib import Path

DB_PATH = str(Path.home() / "Documents" / "Cars2U" / "Cars2U.db")

def connect():
    """
    Establishes a connection to the SQLite database and enables foreign key constraints.

    Returns:
        sqlite3.Connection: A connection object to the database.
    """
    try:
        conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except Exception as e:
        print(f"An error occurred connecting to DB: {e}")
        messagebox.showerror(title="Connection Error", message="Trouble connecting, please try again later")

def close(conn, cursor):
    """
    Closes the provided database connection and cursor.

    Args:
        conn (sqlite3.Connection): The database connection to close.
        cursor (sqlite3.Cursor): The cursor to close.
    """
    cursor.close()
    conn.close()
    
def testLogin(name, password):
    """
    Verifies login credentials and returns user level and person ID if valid.

    Args:
        name (str): The username.
        password (str): The password.

    Returns:
        tuple: (status_code, personID)
            status_code:
                1 = customer login success
                2 = manager login success
                3 = exception occurred
                4 = invalid credentials
            personID: The ID of the person if login successful, else None
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        # Grab the user level (customer or manager) associated with name and password
        query = f"""
            SELECT PersonID, PositionTitle 
            FROM Logon 
            WHERE LOWER(LogonName) = LOWER(?) 
              AND Password = ?
              AND (AccountDisabled IS NULL OR AccountDisabled = 0)
              AND (AccountDeleted IS NULL OR AccountDeleted = 0)
        """
        cursor.execute(query, (name, password))
        
        result = cursor.fetchone()
        
        # If there is an output then login is successful
        if result:
            personID, positionTitle = result
            positionTitle = positionTitle.lower()
            
            if positionTitle == "customer":
                return 1, personID
            elif positionTitle == "manager":
                return 2, personID
        else:
            # Username and password do not exist in DB
            return 4, None

    except Exception as e:
        print(f"An error occurred: {e}")
        return 3  # Indicate failure if an exception occurs
    finally:
        close(conn, cursor)
    
def userExists(username):
    """
    Checks whether a username exists in the Logon table.

    Args:
        username (str): The username to check.

    Returns:
        bool: True if the username exists, False otherwise.
    """
    query = "SELECT * from Logon WHERE LOWER(LogonName) = LOWER(?)"
    try:
        conn = connect()
        cursor = conn.cursor()

        cursor.execute(query, (username,))

        result = cursor.fetchone()

        if result:
            return True
        else:
            return False

    except Exception as e:
        print(f"An error occurred checking if username already exists: {e}")

    finally:
        close(conn, cursor)

def registerUser(data, positionID):
    """
    Registers a new user in the Person and Logon tables with selected security questions.

    Args:
        data (dict): Dictionary containing all user registration information.
        positionID (int): 1 for customer, 2 for manager.

    Returns:
        bool: True if registration succeeded, False otherwise.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        if positionID == 1:
            position = 'customer'
        else:
            position = 'manager'

        # get position ID
        positionQuery = "SELECT PositionID FROM Position WHERE PositionTitle = ?"
        cursor.execute(positionQuery, (position,))
        positionId = cursor.fetchone()[0]

        # populate "person" table with account data
        personQuery = """
            INSERT INTO Person 
            (Title, NameFirst, NameMiddle, NameLast, Suffix, Address1, Address2, Address3, City, Zipcode, State, 
            Email, PhonePrimary, PhoneSecondary, PositionID, PersonDeleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """
        cursor.execute(personQuery,
            data.get("Title"), data["First Name"], data.get("Middle Name"), data["Last Name"], data.get("Suffix"),
            data["Address 1"], data.get("Address 2"), data.get("Address 3"), data["City"], data["Zipcode"], data["State"],
            data.get("Email"), data.get("Phone Primary"), data.get("Phone Secondary"), positionId
        )

        # get last inserted ID (to put into logon table)
        personId = cursor.lastrowid

        # figure out which set of questions the user used
        securityQuestions = []
        selectedQuestions = {
            1: [data.get("Question1"), data.get("Question2"), data.get("Question3")],
            2: [data.get("Question4"), data.get("Question5"), data.get("Question6")],
            3: [data.get("Question7"), data.get("Question8"), data.get("Question9")]
        }
        chosenQuestions = selectedQuestions[data["SelectedSet"]]

        # figure out the answers the user gave (based on question set)
        chosenAnswers = []
        selectedAnswers = {
            1: [data.get("Answer1"), data.get("Answer2"), data.get("Answer3")],
            2: [data.get("Answer4"), data.get("Answer5"), data.get("Answer6")],
            3: [data.get("Answer7"), data.get("Answer8"), data.get("Answer9")]
        }
        chosenAnswers = selectedAnswers[data["SelectedSet"]]

        # get the relevant question id's from the "securityquestion" table
        for question in chosenQuestions:
            questionQuery = "SELECT QuestionID FROM SecurityQuestions WHERE QuestionPrompt = ?"
            cursor.execute(questionQuery, question)
            questionId = cursor.fetchone()
            securityQuestions.append(questionId[0])

        # insert account data into "logon" table
        logonQuery = """
            INSERT INTO Logon 
            (PersonID, LogonName, Password, FirstChallengeQuestion, FirstChallengeAnswer, 
            SecondChallengeQuestion, SecondChallengeAnswer, ThirdChallengeQuestion, ThirdChallengeAnswer, 
            PositionTitle, AccountDisabled, AccountDeleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
            """
        cursor.execute(logonQuery,
            personId, data["Username"], data["Password"],
            securityQuestions[0], chosenAnswers[0],
            securityQuestions[1], chosenAnswers[1],
            securityQuestions[2], chosenAnswers[2],
            position
        )

        # commit changes
        conn.commit()
        return True
    except Exception as e:
        print(f"Could not register user:\n{e}")
        messagebox.showerror(title="Registration Error", message="Could not register user")
    finally:
        close(conn, cursor)

def loadQuestions(username):
    """
    Retrieves the 3 security questions and their answers for the given username.

    Args:
        username (str): The username to lookup.

    Returns:
        tuple: (Question1, Question2, Question3, Answer1, Answer2, Answer3) or None
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = """
            SELECT sq1.QuestionPrompt, sq2.QuestionPrompt, sq3.QuestionPrompt, 
                   l.FirstChallengeAnswer, l.SecondChallengeAnswer, l.ThirdChallengeAnswer
            FROM Logon l
            JOIN SecurityQuestions sq1 ON l.FirstChallengeQuestion = sq1.QuestionID
            JOIN SecurityQuestions sq2 ON l.SecondChallengeQuestion = sq2.QuestionID
            JOIN SecurityQuestions sq3 ON l.ThirdChallengeQuestion = sq3.QuestionID
            WHERE LOWER(l.LogonName) = LOWER(?)
        """

        cursor.execute(query, (username,))
        return cursor.fetchone()
    
    except Exception as e:
        print(f"Error getting security questions: {e}")
        messagebox.showerror(title="Database Error", message="Could not get retrieve security questions from database")
    finally:
        close(conn, cursor)

def changePassword(username, password):
    """
    Changes the password for the given username.

    Args:
        username (str): The username whose password will be changed.
        password (str): The new password.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = "UPDATE Logon SET Password = ? WHERE LOWER(LogonName) = LOWER(?)"
        cursor.execute(query, (password, username))
        
        conn.commit()
        messagebox.showinfo(title="Password Updated", message="Your password has been changed!")

    except Exception as e:
        print(f"Error updating password: {e}")
        messagebox.showerror(title="Database Error", message="Could not update password")

    finally:
        close(conn, cursor)

def getItemByID(itemID):
    """
    Retrieves full item details by InventoryID.

    Args:
        itemID (int): The ID of the item.

    Returns:
        dict: Item data including ID, name, description, price, cost, etc., or None if not found.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = '''
            SELECT i.InventoryID, i.ItemName, i.ItemDescription, i.RetailPrice, i.Cost, i.Quantity, i.RestockThreshold, c.CategoryName, i.ItemImage
            FROM Inventory i
            JOIN Categories c ON i.CategoryID = c.CategoryID
            WHERE i.InventoryID = ?
        '''
        cursor.execute(query, (itemID,))
        row = cursor.fetchone()

        if row:
            return {
                "InventoryID": row[0],
                "ItemName": row[1],
                "ItemDescription": row[2],
                "RetailPrice": float(row[3]),
                "Cost": float(row[4]),
                "Quantity": row[5],
                "RestockThreshold": row[6],
                "CategoryName": row[7],
                "ItemImage": row[8]
            }

    except Exception as e:
        print(f"Error in getItemByID: {e}")
    finally:
        close(conn, cursor)

def getPageInventory(offset, limit):
    """
    Retrieves a page of inventory items.

    Args:
        offset (int): Number of items to skip.
        limit (int): Number of items to retrieve.

    Returns:
        list: List of inventory items as dictionaries.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = '''
            SELECT i.InventoryID, i.ItemName, i.ItemDescription, i.RetailPrice, i.Quantity, c.CategoryName, i.ItemImage
            FROM Inventory i
            JOIN Categories c ON i.CategoryID = c.CategoryID
            WHERE i.Discontinued = 0 AND i.Quantity > 0
            ORDER BY i.InventoryID
            LIMIT ? OFFSET ?
        '''
        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()

        return [{
            "InventoryID": row[0],
            "ItemName": row[1],
            "ItemDescription": row[2],
            "RetailPrice": float(row[3]),
            "Quantity": row[4],
            "CategoryName": row[5],
            "ItemImage": row[6]
        } for row in rows]

    except Exception as e:
        print(f"Error in getPageInventory: {e}")
        return []
    finally:
        close(conn, cursor)

def getInventoryCount():
    """
    Retrieves the total number of active (non-discontinued) items in the Inventory table.

    Returns:
        int: The count of items where Discontinued = 0. Returns 0 if an error occurs.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) 
            FROM Inventory
            WHERE Discontinued = 0""")
        count = cursor.fetchone()[0]
        return count

    except Exception as e:
        print(f"Error getting inventory count: {e}")
        return 0

    finally:
        close(conn, cursor)

def searchInventory(keyword, category, offset, limit):
    """
    Searches the inventory for active items based on a keyword and/or category,
    and returns a paginated list of matching items.

    Args:
        keyword (str): Optional search term to match against item names.
        category (str): Optional category filter; if "All", no category filter is applied.
        offset (int): Number of records to skip (for pagination).
        limit (int): Number of records to return.

    Returns:
        list: A list of dictionaries containing item details. Returns an empty list if no results or an error occurs.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = '''
            SELECT i.InventoryID, i.ItemName, i.ItemDescription, i.RetailPrice,
                   i.Quantity, c.CategoryName, i.ItemImage
            FROM Inventory i
            JOIN Categories c ON i.CategoryID = c.CategoryID
            WHERE i.Discontinued = 0 AND Quantity > 0
        '''

        params = []

        if keyword:
            query += " AND i.ItemName LIKE ?"
            params.append(f"%{keyword}%")

        if category and category != "All":
            query += " AND c.CategoryName = ?"
            params.append(category)

        query += " ORDER BY i.InventoryID LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [{
            "InventoryID": row[0],
            "ItemName": row[1],
            "ItemDescription": row[2],
            "RetailPrice": float(row[3]),
            "Quantity": row[4],
            "CategoryName": row[5],
            "ItemImage": row[6]
        } for row in rows]

    except Exception as e:
        print(f"Error in searchInventory: {e}")
        return []
    finally:
        close(conn, cursor)

def countSearchInventory(keyword, category):
    """
    Counts how many inventory items match the given keyword and category filters.

    Args:
        keyword (str): Optional search term to match against item names.
        category (str): Optional category filter; if "All", no category filter is applied.

    Returns:
        int: The count of matching inventory items. Returns 0 if an error occurs.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = '''
            SELECT COUNT(*)
            FROM Inventory i
            JOIN Categories c ON i.CategoryID = c.CategoryID
            WHERE i.Discontinued = 0 AND Quantity > 0
        '''

        params = []

        if keyword:
            query += " AND i.ItemName LIKE ?"
            params.append(f"%{keyword}%")
        if category and category != "All":
            query += " AND c.CategoryName = ?"
            params.append(category)

        cursor.execute(query, params)
        return cursor.fetchone()[0]
    
    except Exception as e:
        print(f"Error in countSearchInventory: {e}")
        return 0
    finally:
        close(conn, cursor)

def validatePromoCode(code, cartItems=None):
    """
    Validates a promo code by checking if it exists, is within its active date range,
    and (if item-level) applies to an item in the cart.

    Args:
        code (str): The promo code entered by the user.
        cartItems (list, optional): A list of dictionaries representing items in the cart.

    Returns:
        dict or None: A dictionary of discount details if valid, otherwise None.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = '''
            SELECT DiscountID, DiscountCode, Description, DiscountLevel, InventoryID,
                   DiscountType, DiscountPercentage, DiscountDollarAmount,
                   StartDate, ExpirationDate
            FROM Discounts
            WHERE DiscountCode = ?
        '''
        cursor.execute(query, (code,))
        row = cursor.fetchone()

        if row:
            startDate = date.fromisoformat(row[8])
            endDate = date.fromisoformat(row[9])
            today = date.today()

            if (startDate > today) or (endDate < today):
                # Not started or expired
                return None

            discount = {
                "DiscountID": row[0],
                "DiscountCode": row[1],
                "Description": row[2],
                "DiscountLevel": row[3],
                "InventoryID": row[4],
                "DiscountType": row[5],
                "DiscountPercentage": float(row[6]) if row[6] is not None else 0,
                "DiscountDollarAmount": float(row[7]) if row[7] is not None else 0,
                "StartDate": startDate,
                "ExpirationDate": endDate
            }

            # Ensure item in cart if item level discount
            if discount["DiscountLevel"] == 1:
                if not cartItems:
                    return None
                matching = any(item.get("InventoryID") == discount["InventoryID"] for item in cartItems)
                if not matching:
                    return None

            return discount
        else:
            return None

    except Exception as e:
        print(f"Error in validatePromoCode: {e}")
        return None
    finally:
        close(conn, cursor)

def getProductPackages(inventoryID):
    """
    Retrieves all packages associated with a specific inventory item.

    Args:
        inventoryID (int): The ID of the inventory item.

    Returns:
        list: A list of dictionaries with 'name' and 'description' of each package.
              If no packages exist, returns a default 'Standard' package.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = """
            SELECT PackageName, PackageDescription
            FROM ProductPackage
            WHERE InventoryID = ?
        """
        cursor.execute(query, (inventoryID,))
        rows = cursor.fetchall()
        # Return packages - default to "Standard" "Standard configuration"
        return [{"name": row[0], "description": row[1]} for row in rows] if rows else [{"name": "Standard", "description": "Standard configuration"}]

    except Exception as e:
        print(f"Error fetching packages for InventoryID {inventoryID}: {e}")
        return [{"name": "Standard", "description": "Standard configuration"}]
    finally:
        close(conn, cursor)

def getCategories():
    """
    Retrieves all category names from the database.

    Returns:
        list: A list of category names with "All" prepended to the list.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT CategoryName FROM Categories")
        rows = cursor.fetchall()
        return ["All"] + [row[0] for row in rows]
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return ["All"]
    finally:
        close(conn, cursor)

def insertOrder(personID, discountID, ccNumber, expDate, ccv, managerID=None):
    """
    Inserts a new order into the Orders table.

    Args:
        personID (int): The ID of the person placing the order.
        discountID (int): The ID of the discount applied (can be None).
        ccNumber (str): Credit card number.
        expDate (str): Expiration date of the card.
        ccv (str): Credit card security code.
        managerID (int, optional): ID of the manager processing the order.

    Returns:
        int: The newly created OrderID.
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Orders (DiscountID, PersonID, EmployeeID, OrderDate, CC_Number, ExpDate, CCV)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (discountID, personID, managerID, date.today(), ccNumber, expDate, ccv))
    conn.commit()

    # Get the OrderID
    orderID = cursor.lastrowid
    close(conn, cursor)
    return int(orderID)

def insertOrderDetail(orderID, inventoryID, quantity, discountID=None):
    """
    Inserts a record into the OrderDetails table for a given order.

    Args:
        orderID (int): The ID of the order.
        inventoryID (int): The inventory item ID.
        quantity (int): Quantity purchased.
        discountID (int, optional): The discount ID applied to this item.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO OrderDetails (OrderID, InventoryID, DiscountID, Quantity)
            VALUES (?, ?, ?, ?)
        """, (orderID, inventoryID, discountID, quantity))
        conn.commit()
    except Exception as e:
        print(f"Error adding order details to DB: {e}")
    finally:
        close(conn, cursor)

def updateInventoryQuantity(inventoryID, quantityChange):
    """
    Updates the inventory quantity by adding the specified change.

    Args:
        inventoryID (int): The ID of the inventory item.
        quantityChange (int): The amount to add/subtract from inventory.

    Raises:
        Exception: If update fails or stock is insufficient.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Inventory
            SET Quantity = Quantity + ?
            WHERE InventoryID = ?
        """, (quantityChange, inventoryID))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Inventory update failed: {e}")
        raise Exception("Insufficient stock or invalid inventory update.")
    finally:
        close(conn, cursor)

def checkQuantity(inventoryID):
    """
    Returns the current quantity for a specific inventory item.

    Args:
        inventoryID (int): The ID of the item.

    Returns:
        int: The current quantity, or 0 if item is not found.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""SELECT Quantity 
                       FROM Inventory
                       WHERE InventoryID = ?""", (inventoryID,))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            return 0
    except Exception as e:
        print(f"Error in checkQuantity: {e}")
    finally:
        close(conn, cursor)

def removeItem(itemID):
    """
    Marks an inventory item as discontinued.

    Args:
        itemID (int): The ID of the item to discontinue.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = """UPDATE Inventory
            SET Discontinued = 1
            WHERE InventoryID = ?"""
        cursor.execute(query, (itemID,))
        conn.commit()
    except Exception as e:
        print(f"Error removing item: {e}")
    finally:
        close(conn, cursor)

def searchInventoryManager(keyword):
    """
    Allows a manager to search for inventory items by keyword.

    Args:
        keyword (str): The term to search for in item names.

    Returns:
        list: A list of matching inventory items with detailed data.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = '''
            SELECT InventoryID, ItemName, Cost, RetailPrice, Quantity, RestockThreshold, Discontinued
            FROM Inventory
            WHERE ItemName LIKE ?
        '''

        cursor.execute(query, (f"%{keyword}%",))
        rows = cursor.fetchall()

        return [{
            "InventoryID": row[0],
            "ItemName": row[1],
            "Cost": row[2],
            "RetailPrice": row[3],
            "Quantity": row[4],
            "RestockThreshold": row[5],
            "Discontinued": row[6]
        } for row in rows]

    except Exception as e:
        print(f"Error in searchInventory: {e}")
        return []
    finally:
        close(conn, cursor)

def addInventoryItem(name, description, categoryName, cost, retailPrice, quantity, restockThreshold, packages, imageBlob):
    """
    Adds a new inventory item and associated packages to the database.

    Args:
        name (str): Item name.
        description (str): Item description.
        categoryName (str): Category name (created if not exists).
        cost (float): Item cost.
        retailPrice (float): Retail price.
        quantity (int): Starting quantity.
        restockThreshold (int): Minimum threshold to trigger restock alert.
        packages (list): List of packages (dicts with name and description).
        imageBlob (bytes): Binary image data.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        # Get the CategoryID
        categoryQuery = "SELECT CategoryID FROM Categories WHERE CategoryName = ?"
        cursor.execute(categoryQuery, (categoryName,))
        categoryRow = cursor.fetchone()

        if categoryRow:
            categoryID = categoryRow[0]
        else:
            # If category does not exist, create it
            insertCategoryQuery = "INSERT INTO Categories (CategoryName) VALUES (?)"
            cursor.execute(insertCategoryQuery, (categoryName,))
            conn.commit()

            # Get the new category ID
            cursor.execute(categoryQuery, (categoryName,))
            categoryID = cursor.fetchone()[0]

        # Insert into Inventory table
        insertInventoryQuery = """
            INSERT INTO Inventory 
            (ItemName, ItemDescription, CategoryID, RetailPrice, Cost, Quantity, RestockThreshold, ItemImage, Discontinued)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """
        cursor.execute(insertInventoryQuery, (name, description, categoryID, retailPrice, cost, quantity, restockThreshold, imageBlob))
        conn.commit()

        # Get new InventoryID
        inventoryID = cursor.lastrowid

        # Insert packages
        if packages:
            for pkg in packages:
                insertPackageQuery = """
                    INSERT INTO ProductPackage (InventoryID, PackageName, PackageDescription)
                    VALUES (?, ?, ?)
                """
                cursor.execute(insertPackageQuery, (inventoryID, pkg["name"], pkg["description"]))

        conn.commit()

    except Exception as e:
        print(f"Error adding inventory item: {e}")
        messagebox.showerror("Database Error", "There was a problem adding the new product.")
    finally:
        close(conn, cursor)

def checkLowInventory():
    """
    Checks inventory for items below restock threshold and shows a message box
    if any items are found.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = """
            SELECT ItemName, Quantity, RestockThreshold
            FROM Inventory
            WHERE Quantity < RestockThreshold
            AND Discontinued = 0
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            message = "The following products are below their restock threshold:\n\n"
            for itemName, qty, threshold in rows:
                message += f"- {itemName}: {qty} in stock (Threshold: {threshold})\n"
            messagebox.showinfo("Inventory Notification", message)
        else:
            # don't show a box if nothing is low
            pass

    except Exception as e:
        print(f"Error checking low inventory: {e}")
    finally:
        close(conn, cursor)

def getLowInventoryItems():
    """
    Returns a list of all items that are below their restock threshold.

    Returns:
        list: A list of dictionaries containing low-stock item details.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = """
            SELECT InventoryID, ItemName, Quantity, RestockThreshold
            FROM Inventory
            WHERE Quantity < RestockThreshold
            AND Discontinued = 0
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        return [{
            "InventoryID": row[0],
            "ItemName": row[1],
            "Quantity": row[2],
            "RestockThreshold": row[3]
        } for row in rows]

    except Exception as e:
        print(f"Error fetching low inventory items: {e}")
        return []
    finally:
        close(conn, cursor)

def updateInventoryItem(itemID, name, description, categoryName, cost, retailPrice, quantity, restockThreshold, packages, imageBlob):
    """
    Updates an existing inventory item and its associated packages.

    Args:
        itemID (int): The ID of the item to update.
        name (str): New name of the item.
        description (str): New description.
        categoryName (str): Category name (created if not exists).
        cost (float): New cost.
        retailPrice (float): New retail price.
        quantity (int): New quantity.
        restockThreshold (int): New restock threshold.
        packages (list): List of new packages.
        imageBlob (bytes): New image data.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        # Get the CategoryID
        categoryQuery = "SELECT CategoryID FROM Categories WHERE CategoryName = ?"
        cursor.execute(categoryQuery, (categoryName,))
        categoryRow = cursor.fetchone()

        if categoryRow:
            categoryID = categoryRow[0]
        else:
            # If category does not exist, create it
            insertCategoryQuery = "INSERT INTO Categories (CategoryName) VALUES (?)"
            cursor.execute(insertCategoryQuery, (categoryName,))
            conn.commit()
            cursor.execute(categoryQuery, (categoryName,))
            categoryID = cursor.fetchone()[0]

        # Update Inventory Table
        updateInventoryQuery = """
            UPDATE Inventory
            SET ItemName = ?, ItemDescription = ?, CategoryID = ?, RetailPrice = ?, Cost = ?, 
                Quantity = ?, RestockThreshold = ?, ItemImage = ?
            WHERE InventoryID = ?
        """
        cursor.execute(updateInventoryQuery, (name, description, categoryID, retailPrice, cost, quantity, restockThreshold, imageBlob, itemID))

        # Delete old packages
        deletePackagesQuery = "DELETE FROM ProductPackage WHERE InventoryID = ?"
        cursor.execute(deletePackagesQuery, (itemID,))

        # Insert new packages
        if packages:
            for pkg in packages:
                insertPackageQuery = """
                    INSERT INTO ProductPackage (InventoryID, PackageName, PackageDescription)
                    VALUES (?, ?, ?)
                """
                cursor.execute(insertPackageQuery, (itemID, pkg["name"], pkg["description"]))

        conn.commit()

    except Exception as e:
        print(f"Error updating inventory item: {e}")
        messagebox.showerror("Database Error", "There was a problem updating the product.")
    finally:
        close(conn, cursor)

def getAllAccounts():
    """
    Retrieves all user accounts that are not deleted.

    Returns:
        list: A list of dictionaries containing user account details.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = """
            SELECT p.PersonID, l.LogonName, l.PositionTitle, l.AccountDisabled, l.AccountDeleted
            FROM Person p
            JOIN Logon l ON p.PersonID = l.PersonID
            WHERE l.AccountDeleted = 0
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        return [{
            "PersonID": row[0],
            "Username": row[1],
            "Position": row[2],
            "AccountDisabled": row[3],
            "AccountDeleted": row[4]
        } for row in rows]

    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return []
    finally:
        close(conn, cursor)

def disableAccount(personID):
    """
    Disables a user account by setting AccountDisabled to 1.

    Args:
        personID (int): ID of the person whose account is to be disabled.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = """
            UPDATE Logon
            SET AccountDisabled = 1
            WHERE PersonID = ?
        """
        cursor.execute(query, (personID,))
        conn.commit()

    except Exception as e:
        print(f"Error disabling account: {e}")
        messagebox.showerror("Database Error", "Could not disable the account.")
    finally:
        close(conn, cursor)

def getAllUserInfo(personID):
    """
    Retrieves full profile information and security question data for a given user.

    Args:
        personID (int): The ID of the user.

    Returns:
        dict: A dictionary of user profile fields and credentials.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        personQuery = """
            SELECT 
                Title, NameFirst, NameMiddle, NameLast, Suffix, Address1, Address2, Address3, 
                City, Zipcode, State, Email, PhonePrimary, PhoneSecondary, PositionID
            FROM Person
            WHERE PersonID = ?
        """
        cursor.execute(personQuery, (personID,))
        personRow = cursor.fetchone()

        if not personRow:
            return {}

        logonQuery = """
            SELECT 
                LogonName, Password, 
                FirstChallengeQuestion, FirstChallengeAnswer, 
                SecondChallengeQuestion, SecondChallengeAnswer, 
                ThirdChallengeQuestion, ThirdChallengeAnswer, 
                PositionTitle
            FROM Logon
            WHERE PersonID = ?
        """
        cursor.execute(logonQuery, (personID,))
        logonRow = cursor.fetchone()

        if not logonRow:
            return {}

        questions = []
        for questionID in [logonRow[2], logonRow[4], logonRow[6]]:
            questionQuery = "SELECT QuestionPrompt FROM SecurityQuestions WHERE QuestionID = ?"
            cursor.execute(questionQuery, (questionID,))
            result = cursor.fetchone()
            questions.append(result[0] if result else "")

        userInfo = {
            "Title": personRow[0],
            "First Name": personRow[1],
            "Middle Name": personRow[2],
            "Last Name": personRow[3],
            "Suffix": personRow[4],
            "Address 1": personRow[5],
            "Address 2": personRow[6],
            "Address 3": personRow[7],
            "City": personRow[8],
            "Zipcode": personRow[9],
            "State": personRow[10],
            "Email": personRow[11],
            "Phone Primary": personRow[12],
            "Phone Secondary": personRow[13],
            "Username": logonRow[0],
            "Password": logonRow[1],
            "Security Question 1": questions[0],
            "Security Answer 1": logonRow[3],
            "Security Question 2": questions[1],
            "Security Answer 2": logonRow[5],
            "Security Question 3": questions[2],
            "Security Answer 3": logonRow[7],
            "Position": logonRow[8]
        }

        return userInfo

    except Exception as e:
        print(f"Error fetching full user data: {e}")
        return {}
    finally:
        close(conn, cursor)

def updateUserProfile(personID, data, positionID, position, imageBlob):
    """
    Updates a user's profile information in the Person and Logon tables.

    Args:
        personID (int): The user's unique identifier.
        data (dict): Dictionary containing updated profile information.
        positionID (int): Position ID (e.g., customer or manager).
        position (str): Position title (e.g., "customer", "manager").
        imageBlob (bytes): Binary image data for the user's profile picture.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        # Update Person table
        updatePersonQuery = """
            UPDATE Person
            SET
                Title = ?,
                NameFirst = ?,
                NameMiddle = ?,
                NameLast = ?,
                Suffix = ?,
                Address1 = ?,
                Address2 = ?,
                Address3 = ?,
                City = ?,
                Zipcode = ?,
                State = ?,
                Email = ?,
                PhonePrimary = ?,
                PhoneSecondary = ?,
                PositionID = ?,
                Image = ?
            WHERE PersonID = ?
        """
        cursor.execute(updatePersonQuery, (
            data.get("Title"),
            data.get("First Name"),
            data.get("Middle Name"),
            data.get("Last Name"),
            data.get("Suffix"),
            data.get("Address 1"),
            data.get("Address 2"),
            data.get("Address 3"),
            data.get("City"),
            data.get("Zipcode"),
            data.get("State"),
            data.get("Email"),
            data.get("Phone Primary"),
            data.get("Phone Secondary"),
            positionID,
            imageBlob,
            personID
        ))

        # Update Logon table
        updateLogonQuery = """
            UPDATE Logon
            SET
                Password = ?,
                FirstChallengeAnswer = ?,
                SecondChallengeAnswer = ?,
                ThirdChallengeAnswer = ?,
                PositionTitle = ?
            WHERE PersonID = ?
        """
        cursor.execute(updateLogonQuery, (
            data.get("Password"),
            data.get("Security Answer 1"),
            data.get("Security Answer 2"),
            data.get("Security Answer 3"),
            position, personID
        ))
        conn.commit()
        
    except Exception as e:
        print(f"Error updating user profile: {e}")
        messagebox.showerror("Update Error", "Could not update user profile.")
    finally:
        close(conn, cursor)

def getAllPromos():
    """
    Retrieves all promotional discounts from the Discounts table.

    Returns:
        list: A list of dictionaries containing promotion details including associated item name.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        query = """
            SELECT d.DiscountID, d.DiscountCode, d.Description, d.DiscountLevel, 
                   d.InventoryID, d.DiscountType, d.DiscountPercentage, d.DiscountDollarAmount,
                   d.StartDate, d.ExpirationDate, i.ItemName
            FROM Discounts d
            LEFT JOIN Inventory i ON d.InventoryID = i.InventoryID
            ORDER BY d.ExpirationDate
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [{
            "DiscountID": row[0],
            "DiscountCode": row[1],
            "Description": row[2],
            "DiscountLevel": row[3],
            "InventoryID": row[4],
            "DiscountType": row[5],
            "DiscountPercentage": row[6],
            "DiscountDollarAmount": row[7],
            "StartDate": row[8],
            "ExpirationDate": row[9],
            "ItemName": row[10]
        } for row in rows]
    except Exception as e:
        print(f"Error getting promos: {e}")
        return []
    finally:
        close(conn, cursor)

def insertPromoCode(code, description, level, inventoryID, discountType, value, startDate, endDate):
    """
    Inserts a new promotional discount into the Discounts table.

    Args:
        code (str): The unique promo code.
        description (str): Description of the promotion.
        level (int): Discount level (0 = cart level, 1 = item level).
        inventoryID (int or None): ID of the inventory item the promo applies to (or None for cart-wide).
        discountType (int): 0 = percentage, 1 = dollar amount.
        value (float): Value of the discount.
        startDate (str): Promotion start date in ISO format.
        endDate (str): Promotion end date in ISO format.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        if discountType == 0:
            discountPercentage = float(value)
            discountDollarAmount = None
        else:
            discountPercentage = None
            discountDollarAmount = float(value)
        
        query = """
            INSERT INTO Discounts
            (DiscountCode, Description, DiscountLevel, InventoryID, DiscountType,
             DiscountPercentage, DiscountDollarAmount, StartDate, ExpirationDate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (code, description, level, inventoryID, discountType,
                               discountPercentage, discountDollarAmount, startDate, endDate))
        conn.commit()
    except Exception as e:
        print(f"Error inserting promo: {e}")
    finally:
        close(conn, cursor)

def deletePromoCode(discountID):
    """
    Deletes a promotion from the Discounts table by its ID.

    Args:
        discountID (int): The ID of the discount to delete.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        query = "DELETE FROM Discounts WHERE DiscountID = ?"
        cursor.execute(query, (discountID,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting promo: {e}")
    finally:
        close(conn, cursor)

def getSalesByDate(date):
    """
    Retrieves all sales that occurred on a specific date.

    Args:
        date (str): The date in 'YYYY-MM-DD' format.

    Returns:
        list: A list of sales with subtotal, tax, and total amounts per order.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        query = """
             SELECT o.OrderID, o.OrderDate, 
                   SUM(i.RetailPrice * od.Quantity) AS Subtotal,
                   SUM(i.RetailPrice * od.Quantity) * 0.0825 AS Tax,
                   SUM(i.RetailPrice * od.Quantity) * 1.0825 AS Total
            FROM Orders o
            JOIN OrderDetails od ON o.OrderID = od.OrderID
            JOIN Inventory i ON od.InventoryID = i.InventoryID
            WHERE date(o.OrderDate) = ?
            GROUP BY o.OrderID, o.OrderDate
        """
        cursor.execute(query, (date,))
        rows = cursor.fetchall()
        return [{
            "OrderID": row[0],
            "OrderDate": row[1],
            "Subtotal": row[2],
            "Tax": row[3],
            "Total": row[4]
        } for row in rows]
    except Exception as e:
        print(f"Error in getSalesByDate: {e}")
        return []
    finally:
        close(conn, cursor)

def getSalesByWeek(startDate):
    """
    Retrieves all sales for a 7-day period starting from the given date.

    Args:
        startDate (datetime.date): The start date of the week.

    Returns:
        list: A list of sales records with totals for each order.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        endDate = startDate + datetime.timedelta(days=6)
        query = """
            SELECT o.OrderID, o.OrderDate, 
                   SUM(i.RetailPrice * od.Quantity) AS Subtotal,
                   SUM(i.RetailPrice * od.Quantity) * 0.0825 AS Tax,
                   SUM(i.RetailPrice * od.Quantity) * 1.0825 AS Total
            FROM Orders o
            JOIN OrderDetails od ON o.OrderID = od.OrderID
            JOIN Inventory i ON od.InventoryID = i.InventoryID
             WHERE date(o.OrderDate) BETWEEN date(?) AND date(?)
            GROUP BY o.OrderID, o.OrderDate
        """
        cursor.execute(query, (startDate, endDate))
        rows = cursor.fetchall()
        return [{
            "OrderID": row[0],
            "OrderDate": row[1],
            "Subtotal": row[2],
            "Tax": row[3],
            "Total": row[4]
        } for row in rows]
    except Exception as e:
        print(f"Error in getSalesByWeek: {e}")
        return []
    finally:
        close(conn, cursor)

def getSalesByMonth(month, year):
    """
    Retrieves all sales for a given month and year.

    Args:
        month (str): The month in 'MM' format.
        year (str): The year in 'YYYY' format.

    Returns:
        list: A list of sales records for the specified month.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        query = """
            SELECT o.OrderID, o.OrderDate, 
                   SUM(i.RetailPrice * od.Quantity) AS Subtotal,
                   SUM(i.RetailPrice * od.Quantity) * 0.0825 AS Tax,
                   SUM(i.RetailPrice * od.Quantity) * 1.0825 AS Total
            FROM Orders o
            JOIN OrderDetails od ON o.OrderID = od.OrderID
            JOIN Inventory i ON od.InventoryID = i.InventoryID
            WHERE strftime('%m', o.OrderDate) = ? AND strftime('%Y', o.OrderDate) = ?
            GROUP BY o.OrderID, o.OrderDate
        """

        cursor.execute(query, (month, year))
        rows = cursor.fetchall()
        return [{
            "OrderID": row[0],
            "OrderDate": row[1],
            "Subtotal": row[2],
            "Tax": row[3],
            "Total": row[4]
        } for row in rows]
    except Exception as e:
        print(f"Error in getSalesByMonth: {e}")
        return []
    finally:
        close(conn, cursor)

def getInventoryForSale():
    """
    Retrieves all inventory items that are not discontinued.

    Returns:
        list: A list of dictionaries with inventory item details.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        query = """
            SELECT InventoryID, ItemName, Cost, RetailPrice, Quantity, RestockThreshold, Discontinued
            FROM Inventory
            WHERE Discontinued = 0
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [{
            "InventoryID": row[0],
            "ItemName": row[1],
            "Cost": row[2],
            "RetailPrice": row[3],
            "Quantity": row[4],
            "RestockThreshold": row[5],
            "Discontinued": row[6]
        } for row in rows]
    except Exception as e:
        print(f"Error in getInventoryForSale: {e}")
        return []
    finally:
        close(conn, cursor)

def getInventoryRestock():
    """
    Retrieves inventory items where quantity is less than or equal to the restock threshold.

    Returns:
        list: A list of items that need to be restocked.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        query = """
            SELECT InventoryID, ItemName, Cost, RetailPrice, Quantity, RestockThreshold, Discontinued
            FROM Inventory
            WHERE Quantity <= RestockThreshold
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [{
            "InventoryID": row[0],
            "ItemName": row[1],
            "Cost": row[2],
            "RetailPrice": row[3],
            "Quantity": row[4],
            "RestockThreshold": row[5],
            "Discontinued": row[6]
        } for row in rows]
    except Exception as e:
        print(f"Error in getInventoryRestock: {e}")
        return []
    finally:
        close(conn, cursor)

def getAllInventoryIncludingDiscontinued():
    """
    Retrieves all inventory items including those that are discontinued.

    Returns:
        list: A list of dictionaries representing all inventory items.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        query = """
            SELECT InventoryID, ItemName, Cost, RetailPrice, Quantity, RestockThreshold, Discontinued
            FROM Inventory
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [{
            "InventoryID": row[0],
            "ItemName": row[1],
            "Cost": row[2],
            "RetailPrice": row[3],
            "Quantity": row[4],
            "RestockThreshold": row[5],
            "Discontinued": row[6]
        } for row in rows]
    except Exception as e:
        print(f"Error in getAllInventoryIncludingDiscontinued: {e}")
        return []
    finally:
        close(conn, cursor)

def searchCustomerPOS(keyword, method):
    """
    Searches for customer records based on a keyword and method.

    Args:
        keyword (str): The search term (email, phone, name, etc.).
        method (str): The method of search. One of:
            - "Email"
            - "Phone"
            - "Invoice"
            - "First Name"
            - "Last Name"
            - "MemberID"

    Returns:
        list: A list of matching customer records with contact information.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        if method == "Email":
            query = """
                SELECT PersonID, NameFirst, NameLast, Email, PhonePrimary
                FROM Person
                WHERE Email LIKE ?
            """
            params = (f"%{keyword}%",)
        
        elif method == "Phone":
            query = """
                SELECT PersonID, NameFirst, NameLast, Email, PhonePrimary
                FROM Person
                WHERE PhonePrimary LIKE ? OR PhoneSecondary LIKE ?
            """
            params = (f"%{keyword}%", f"%{keyword}%")
        
        elif method == "Invoice":  # Search by OrderID
            query = """
                SELECT p.PersonID, p.NameFirst, p.NameLast, p.Email, p.PhonePrimary
                FROM Orders o
                JOIN Person p ON o.PersonID = p.PersonID
                WHERE o.OrderID = ?
            """
            params = (keyword,)
        
        elif method == "First Name":
            query = """
                SELECT PersonID, NameFirst, NameLast, Email, PhonePrimary
                FROM Person
                WHERE NameFirst LIKE ?
            """
            params = (f"%{keyword}%",)
        
        elif method == "Last Name":
            query = """
                SELECT PersonID, NameFirst, NameLast, Email, PhonePrimary
                FROM Person
                WHERE NameLast LIKE ?
            """
            params = (f"%{keyword}%",)
        
        elif method == "MemberID":  # Search by PersonID
            query = """
                SELECT PersonID, NameFirst, NameLast, Email, PhonePrimary
                FROM Person
                WHERE PersonID = ?
            """
            params = (keyword,)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [{
            "PersonID": row[0],
            "FirstName": row[1],
            "LastName": row[2],
            "Email": row[3],
            "Phone": row[4]
        } for row in rows]

    except Exception as e:
        print(f"Error in searchCustomerPOS: {e}")
        return []
    finally:
        close(conn, cursor)

def getAvailableDiscounts(cartItems):
    """
    Retrieves all available discounts (cart and item level) that apply to the current cart.

    Args:
        cartItems (list): A list of cart item dictionaries with 'InventoryID' keys.

    Returns:
        list: A list of applicable discount dictionaries with details and calculated amounts.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        inventoryIDs = [str(item['InventoryID']) for item in cartItems]

        query = """
            SELECT d.DiscountID, d.DiscountCode, d.DiscountType, d.DiscountPercentage, d.DiscountDollarAmount,
                   d.DiscountLevel, d.InventoryID, i.ItemName
            FROM Discounts d
            LEFT JOIN Inventory i ON d.InventoryID = i.InventoryID
            WHERE d.ExpirationDate >= date('now')
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        available = []
        for row in rows:
            discountLevel = row[5]
            inventoryID = row[6]

            if discountLevel == 0:  # Cart level discount applies always
                amount = (row[3] if row[2] == 0 else row[4])  # Percent or Dollar
                available.append({
                    "DiscountID": row[0],
                    "DiscountCode": row[1],
                    "DiscountType": row[2],
                    "DiscountPercentage": row[3],
                    "DiscountDollarAmount": row[4],
                    "DiscountLevel": row[5],
                    "InventoryID": row[6],
                    "ItemName": row[7],
                    "DiscountAmount": amount
                })
            elif discountLevel == 1 and str(inventoryID) in inventoryIDs:
                # Item level discount but the item exists in the cart
                amount = (row[3] if row[2] == 0 else row[4])  # Percent or Dollar
                available.append({
                    "DiscountID": row[0],
                    "DiscountCode": row[1],
                    "DiscountType": row[2],
                    "DiscountPercentage": row[3],
                    "DiscountDollarAmount": row[4],
                    "DiscountLevel": row[5],
                    "InventoryID": row[6],
                    "ItemName": row[7],
                    "DiscountAmount": amount
                })

        return available

    except Exception as e:
        print(f"Error in getAvailableDiscounts: {e}")
        return []
    finally:
        close(conn, cursor)

def getManagerNameByOrder(orderID):
    """
    Retrieves the name of the manager (employee) associated with a specific order.

    Args:
        orderID (int): The ID of the order.

    Returns:
        str: The full name of the manager or "N/A" if not found.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.NameFirst, p.NameLast
            FROM Orders o
            LEFT JOIN Person p ON o.EmployeeID = p.PersonID
            WHERE o.OrderID = ?
        """, (orderID,))
        row = cursor.fetchone()
        if row and row[0]:
            return f"{row[0]} {row[1]}"
        else:
            return "N/A"
    except Exception as e:
        print(f"Error fetching manager name: {e}")
        return "N/A"
    finally:
        close(conn, cursor)

def getOrdersByCustomer(personID):
    """
    Retrieves all orders placed by a specific customer.

    Args:
        personID (int): The ID of the customer.

    Returns:
        list: A list of dictionaries with order details such as OrderID, InventoryID,
              Quantity, DiscountID, and OrderDate.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        query = """
            SELECT o.OrderID, od.InventoryID, od.Quantity, od.DiscountID, o.OrderDate
            FROM Orders o
            JOIN OrderDetails od ON o.OrderID = od.OrderID
            WHERE o.PersonID = ?
            ORDER BY o.OrderDate DESC
        """
        cursor.execute(query, (personID,))
        rows = cursor.fetchall()

        return [{
            "OrderID": row[0],
            "InventoryID": row[1],
            "Quantity": row[2],
            "DiscountID": row[3] if row[3] is not None else "N/A",
            "OrderDate": row[4] if isinstance(row[4], str) else row[4].strftime("%m/%d/%Y")
        } for row in rows]

    except Exception as e:
        print(f"Error fetching customer orders: {e}")
        return []
    finally:
        close(conn, cursor)

def addFavorite(personID, inventoryID):
    """
    Adds an inventory item to a user's favorites if it is not already present.

    Args:
        personID (int): The ID of the user.
        inventoryID (int): The ID of the item to favorite.

    Returns:
        bool: True if the item was added, False if it already existed or an error occurred.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(SortOrder), 0) FROM Favorites WHERE PersonID = ?", (personID,))
        maxSort = cursor.fetchone()[0] or 0

        # Check if already exists
        cursor.execute("SELECT 1 FROM Favorites WHERE PersonID = ? AND InventoryID = ?", (personID, inventoryID))
        if cursor.fetchone():
            return False

        cursor.execute("""
            INSERT INTO Favorites (PersonID, InventoryID, SortOrder)
            VALUES (?, ?, ?)
        """, (personID, inventoryID, maxSort + 1))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding favorite: {e}")
        return False
    finally:
        close(conn, cursor)

def removeFavorite(personID, inventoryID):
    """
    Removes an inventory item from a user's favorites list.

    Args:
        personID (int): The ID of the user.
        inventoryID (int): The ID of the item to remove.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM Favorites WHERE PersonID = ? AND InventoryID = ?", (personID, inventoryID))
        conn.commit()
    except Exception as e:
        print(f"Error removing favorite: {e}")
    finally:
        close(conn, cursor)

def getFavorites(personID):
    """
    Retrieves all favorite items for a specific user.

    Args:
        personID (int): The ID of the user.

    Returns:
        list: A list of tuples containing FavoriteID, SortOrder, InventoryID, ItemName, 
              ItemDescription, RetailPrice, ItemImage, and Note.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.FavoriteID, f.SortOrder, i.InventoryID, i.ItemName, i.ItemDescription, 
                   i.RetailPrice, i.ItemImage, f.Note
            FROM Favorites f
            JOIN Inventory i ON f.InventoryID = i.InventoryID
            WHERE f.PersonID = ?
            ORDER BY f.SortOrder ASC
        """, (personID,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching favorites: {e}")
        return []
    finally:
        close(conn, cursor)

def updateSortOrder(favoriteID, newSortOrder):
    """
    Updates the sort order of a favorite item.

    Args:
        favoriteID (int): The ID of the favorite record.
        newSortOrder (int): The new sort order value to assign.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE Favorites SET SortOrder = ? WHERE FavoriteID = ?", (newSortOrder, favoriteID))
        conn.commit()
    except Exception as e:
        print(f"Error updating sort order: {e}")
    finally:
        close(conn, cursor)

def updateNote(favoriteID, note):
    """
    Updates the note associated with a favorite item.

    Args:
        favoriteID (int): The ID of the favorite record.
        note (str): The note text to save.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE Favorites SET Note = ? WHERE FavoriteID = ?", (note, favoriteID))
        conn.commit()
    except Exception as e:
        print(f"Error updating favorite note: {e}")
    finally:
        close(conn, cursor)

def getNote(favoriteID):
    """
    Retrieves the saved note for a specific favorite item.

    Args:
        favoriteID (int): The ID of the favorite record.

    Returns:
        str or None: The note text if available, otherwise None.
    """
    try:
        conn = connect()
        cursor = conn.cursor()

        cursor.execute("SELECT Note FROM Favorites WHERE FavoriteID = ?",(favoriteID,))
        row = cursor.fetchone()
        return row[0]
    except Exception as e:
        print(f"Error fetching favorites: {e}")
        return
    finally:
        close(conn, cursor)