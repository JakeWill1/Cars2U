import sqlite3
import os
from pathlib import Path
import sys

DB_FOLDER = Path.home() / "Documents" / "Cars2U"
DB_FOLDER.mkdir(parents=True, exist_ok=True)
DB_NAME = str(DB_FOLDER / "Cars2U.db")

def createLocalDatabase():
    """
    Creates and populates the local SQLite database for the Cars2U application if it doesn't already exist.
    """
    needsInit = True
    if os.path.exists(DB_NAME):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Inventory'")
            if cursor.fetchone():
                needsInit = False  # Inventory table exists, DB is likely valid
        except Exception as e:
            print(f"Error checking DB schema: {e}")
        finally:
            cursor.close()
            conn.close()

    if not needsInit:
        return

    # Build DB from scratch
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Position table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Position (
            PositionID INTEGER PRIMARY KEY AUTOINCREMENT,
            PositionTitle TEXT NOT NULL
        );
    """)

    # Person table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Person (
            PersonID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT,
            NameFirst TEXT NOT NULL,
            NameMiddle TEXT,
            NameLast TEXT NOT NULL,
            Suffix TEXT,
            Address1 TEXT NOT NULL,
            Address2 TEXT,
            Address3 TEXT,
            City TEXT NOT NULL,
            Zipcode TEXT NOT NULL,
            State TEXT NOT NULL,
            Email TEXT,
            PhonePrimary TEXT,
            PhoneSecondary TEXT,
            Image BLOB,
            PositionID INTEGER NOT NULL,
            PersonDeleted INTEGER,
            FOREIGN KEY (PositionID) REFERENCES Position(PositionID)
        );
    """)

    # SecurityQuestions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SecurityQuestions (
            QuestionID INTEGER PRIMARY KEY AUTOINCREMENT,
            SetID INTEGER NOT NULL,
            QuestionPrompt TEXT NOT NULL
        );
    """)

    # Logon table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Logon (
            LogonID INTEGER PRIMARY KEY AUTOINCREMENT,
            PersonID INTEGER NOT NULL,
            LogonName TEXT NOT NULL UNIQUE,
            Password TEXT NOT NULL,
            FirstChallengeQuestion INTEGER NOT NULL,
            FirstChallengeAnswer TEXT NOT NULL,
            SecondChallengeQuestion INTEGER NOT NULL,
            SecondChallengeAnswer TEXT NOT NULL,
            ThirdChallengeQuestion INTEGER NOT NULL,
            ThirdChallengeAnswer TEXT NOT NULL,
            PositionTitle TEXT NOT NULL,
            AccountDisabled INTEGER,
            AccountDeleted INTEGER,
            FOREIGN KEY (PersonID) REFERENCES Person(PersonID),
            FOREIGN KEY (FirstChallengeQuestion) REFERENCES SecurityQuestions(QuestionID),
            FOREIGN KEY (SecondChallengeQuestion) REFERENCES SecurityQuestions(QuestionID),
            FOREIGN KEY (ThirdChallengeQuestion) REFERENCES SecurityQuestions(QuestionID)
        );
    """)

    # Categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Categories (
            CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
            CategoryName TEXT NOT NULL,
            CategoryDescription TEXT
        );
    """)

    # Inventory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Inventory (
            InventoryID INTEGER PRIMARY KEY AUTOINCREMENT,
            ItemName TEXT NOT NULL,
            ItemDescription TEXT NOT NULL,
            CategoryID INTEGER NOT NULL,
            RetailPrice REAL NOT NULL,
            Cost REAL NOT NULL,
            Quantity INTEGER NOT NULL CHECK (Quantity >= 0),
            RestockThreshold INTEGER NOT NULL CHECK (RestockThreshold >= 0),
            ItemImage BLOB,
            Discontinued INTEGER,
            FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
        );
    """)

    # Discounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Discounts (
            DiscountID INTEGER PRIMARY KEY AUTOINCREMENT,
            DiscountCode TEXT NOT NULL,
            Description TEXT NOT NULL,
            DiscountLevel INTEGER NOT NULL,
            InventoryID INTEGER,
            DiscountType INTEGER NOT NULL,
            DiscountPercentage REAL,
            DiscountDollarAmount REAL,
            StartDate TEXT,
            ExpirationDate TEXT NOT NULL,
            FOREIGN KEY (InventoryID) REFERENCES Inventory(InventoryID)
        );
    """)

    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Orders (
            OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
            DiscountID INTEGER,
            PersonID INTEGER NOT NULL,
            EmployeeID INTEGER,
            OrderDate TEXT NOT NULL,
            CC_Number TEXT,
            ExpDate TEXT,
            CCV TEXT,
            FOREIGN KEY (DiscountID) REFERENCES Discounts(DiscountID),
            FOREIGN KEY (PersonID) REFERENCES Person(PersonID),
            FOREIGN KEY (EmployeeID) REFERENCES Person(PersonID)
        );
    """)

    # OrderDetails table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS OrderDetails (
            OrderDetailsID INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderID INTEGER NOT NULL,
            InventoryID INTEGER NOT NULL,
            DiscountID INTEGER,
            Quantity INTEGER NOT NULL,
            FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
            FOREIGN KEY (InventoryID) REFERENCES Inventory(InventoryID),
            FOREIGN KEY (DiscountID) REFERENCES Discounts(DiscountID)
        );
    """)

    # ProductPackage table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ProductPackage (
            PackageID INTEGER PRIMARY KEY AUTOINCREMENT,
            InventoryID INTEGER NOT NULL,
            PackageName TEXT NOT NULL,
            PackageDescription TEXT NOT NULL,
            FOREIGN KEY (InventoryID) REFERENCES Inventory(InventoryID) ON DELETE CASCADE
        );
    """)

    # Favorite table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Favorites (
            FavoriteID INTEGER PRIMARY KEY AUTOINCREMENT,
            PersonID INTEGER NOT NULL,
            InventoryID INTEGER NOT NULL,
            SortOrder INTEGER NOT NULL,
            Note TEXT,
            FOREIGN KEY (PersonID) REFERENCES Person(PersonID) ON DELETE CASCADE
            FOREIGN KEY (InventoryID) REFERENCES Inventory(InventoryID) ON DELETE CASCADE
        );
    """)

    connection.commit()
    connection.close()
    print("Cars2U.db created successfully.")

    populateDatabase()
    populateImages()

def populateDatabase():
    """
    Inserts default seed data into the Cars2U database. This includes:
    - Security questions
    - Positions (customer, manager)
    - One customer and one manager with logins for demonstration (Username: 'customer' or 'manager' Password: 'Password1')
    - Vehicle categories and inventory entries
    - Product packages
    - Discount codes
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Security Questions
    cursor.execute("""
                INSERT INTO SecurityQuestions
                (SetID, QuestionPrompt)
                VALUES
                (1, 'What is your favorite Color?'),
                (1, 'Your favorite Toy''s name?' ),
                (1, 'Your Pet''s name?' ),
                (2, 'Your Home Town name?'),
                (2, 'Your mother''s first name?'),
                (2, 'Your favorite Football Team?'),
                (3, 'What is your favorite food?'),
                (3, 'Favorite place to vacation?'),
                (3, 'Name of your favorite book?');
            """)

    # Position
    cursor.execute("""
                insert into Position
                (PositionTitle)
                values
                ('customer'),
                ('manager')
            """)

    # Insert manager
    cursor.execute("""
        INSERT INTO Person (Title, NameFirst, NameMiddle, NameLast, Suffix, Address1, Address2, Address3, City, Zipcode, State, Email, PhonePrimary, PhoneSecondary, Image, PositionID, PersonDeleted) VALUES
        (null, 'manager', null, 'test', NULL, '456 Elm St', NULL, NULL, 'test', '90001', 'Tx', 'manager@example.com', '1234567890', NULL, NULL, 2, 0)
    """)
    managerId = cursor.lastrowid

    # Insert customer
    cursor.execute("""
        INSERT INTO Person (Title, NameFirst, NameMiddle, NameLast, Suffix, Address1, Address2, Address3, City, Zipcode, State, Email, PhonePrimary, PhoneSecondary, Image, PositionID, PersonDeleted) VALUES
        (null, 'customer', null, 'test', NULL, '789 Oak St', NULL, NULL, 'test', '60601', 'Tx', 'customer@example.com', '1234567890', NULL, NULL, 1, 0)
    """)
    customerId = cursor.lastrowid

    # Logon
    cursor.execute(f"""
        INSERT INTO Logon (PersonID, LogonName, Password, FirstChallengeQuestion, FirstChallengeAnswer, SecondChallengeQuestion, SecondChallengeAnswer, ThirdChallengeQuestion, ThirdChallengeAnswer, PositionTitle, AccountDisabled, AccountDeleted) VALUES
        ({managerId}, 'manager', 'Password1', 3, 'test', 4, 'test', 5, 'test', 'manager', 0, 0),
        ({customerId}, 'customer', 'Password1', 6, 'test', 7, 'test', 8, 'test', 'customer', 0, 0)
    """)

    # Categories
    cursor.execute("""
                INSERT INTO Categories (CategoryName, CategoryDescription) VALUES
                ('SUVs', 'Roomy, versatile all-rounders'),
                ('sedans', 'Sleek, comfy daily drivers'),
                ('trucks', 'Strong haulers for tough jobs'),
                ('minivans', 'Family-friendly transport'),
                ('electric', 'Quiet, clean, plug-in power');
            """)

    # Inventory
    cursor.execute("""
                INSERT INTO Inventory 
                (ItemName, ItemDescription, CategoryID, RetailPrice, Cost, Quantity, RestockThreshold, ItemImage, Discontinued) 
                VALUES
                -- Trucks
                ('Ford F-150', 'The Ford F-150 is a full-size pickup truck known for its strength, versatility, and reliability.', 3, 30000, 25000, 10, 2, NULL, 0),
                ('Ram 1500', 'A capable and refined pickup with a smooth ride and strong towing capabilities.', 3, 32000, 26000, 8, 2, NULL, 0),
                ('Chevrolet Silverado', 'Chevy’s rugged full-size truck with a powerful engine lineup and solid utility.', 3, 31000, 25500, 6, 2, NULL, 0),
                ('GMC Sierra', 'A premium pickup truck offering powerful towing and modern tech features.', 3, 34000, 27000, 5, 2, NULL, 0),
                ('Toyota Tundra', 'A durable and reliable full-size truck with strong off-road capability.', 3, 35000, 28000, 4, 2, NULL, 0),

                -- SUVs
                ('Honda CR-V', 'A compact SUV with spacious interior, excellent fuel economy, and modern tech.', 1, 28000, 23000, 12, 2, NULL, 0),
                ('Toyota RAV4', 'Toyota’s reliable SUV featuring strong safety ratings and efficient performance.', 1, 29000, 23500, 11, 2, NULL, 0),
                ('Ford Explorer', 'A midsize SUV offering 3 rows of seating, ample cargo space, and smooth performance.', 1, 35000, 30000, 7, 2, NULL, 0),
                ('Jeep Grand Cherokee', 'An SUV blending luxury and off-road performance for all terrains.', 1, 40000, 34000, 5, 2, NULL, 0),
                ('Mazda CX-5', 'A stylish compact SUV with athletic handling and upscale cabin.', 1, 29500, 24500, 7, 2, NULL, 0),

                -- Sedans
                ('Toyota Camry', 'A comfortable and fuel-efficient sedan with a reputation for reliability.', 2, 27000, 22000, 9, 2, NULL, 0),
                ('Honda Accord', 'A spacious, fun-to-drive midsize sedan with a strong value proposition.', 2, 26500, 21500, 8, 2, NULL, 0),
                ('Nissan Altima', 'A stylish sedan with optional AWD and smooth ride quality.', 2, 26000, 21000, 6, 2, NULL, 0),
                ('Hyundai Sonata', 'An elegant midsize sedan with modern tech and great warranty.', 2, 25500, 20500, 7, 2, NULL, 0),
                ('Kia K5', 'A bold-looking sedan offering turbocharged performance and advanced safety tech.', 2, 25800, 20800, 6, 2, NULL, 0),

                -- Minivans
                ('Chrysler Pacifica', 'A family-oriented minivan with premium features and hybrid options.', 4, 35000, 29000, 5, 2, NULL, 0),
                ('Toyota Sienna', 'A reliable, fuel-efficient minivan with optional AWD and hybrid engine.', 4, 36000, 29500, 4, 2, NULL, 0),
                ('Honda Odyssey', 'Known for comfort and space, the Odyssey is a top family van choice.', 4, 35500, 29200, 6, 2, NULL, 0),
                ('Kia Carnival', 'A modern minivan with SUV-like looks and high-end tech.', 4, 34000, 28500, 6, 2, NULL, 0),
                ('Chrysler Voyager', 'An affordable and practical minivan designed for family travel.', 4, 32000, 27500, 3, 2, NULL, 0),

                -- Electric
                ('Tesla Model 3', 'A fully electric sedan offering impressive range, acceleration, and tech.', 5, 42000, 37000, 10, 2, NULL, 0),
                ('Nissan Leaf', 'An affordable electric hatchback with nimble handling and smooth ride.', 5, 31000, 27000, 9, 2, NULL, 0),
                ('Ford Mustang Mach-E', 'A sporty electric SUV that delivers performance and style.', 5, 45000, 39000, 7, 2, NULL, 0),
                ('Chevrolet Bolt EV', 'A compact electric vehicle with great value and solid range.', 5, 29000, 25000, 8, 2, NULL, 0),
                ('Hyundai Ioniq 5', 'A futuristic electric crossover with ultra-fast charging and a spacious cabin.', 5, 48000, 40000, 5, 2, NULL, 0);
            """)

    # Product Package
    cursor.execute("""
                INSERT INTO ProductPackage (InventoryID, PackageName, PackageDescription) VALUES
                (105, 'Base', 'Efficient 2WD version with cloth interior.'),
                (105, 'Touring', 'AWD, navigation system, and moonroof.'),
                (120, 'Standard Range', 'Basic features and range.'),
                (120, 'Long Range', 'Extended battery range and premium sound.'),
                (120, 'Performance', 'High-speed acceleration and track mode.'),
                (107, 'XLT', 'All-around family package.'),
                (107, 'Limited', 'Heated seats, navigation, and advanced safety.'),
                (107, 'Platinum', 'Premium interior, AWD, and towing upgrades.'),
                (110, 'LE', 'Base 4-cylinder model.'),
                (110, 'SE', 'Sport trim with paddle shifters and firmer suspension.'),
                (124, 'SE Standard', 'Entry-level EV features.'),
                (124, 'SEL', 'Heated front seats and power liftgate.'),
                (124, 'Limited', 'Premium features including glass roof and HUD.');
            """)

    # Discounts
    cursor.execute("""
                INSERT INTO Discounts 
                (DiscountCode, Description, DiscountLevel, InventoryID, DiscountType, DiscountPercentage, DiscountDollarAmount, StartDate, ExpirationDate) 
                VALUES
                ('SAVE10', '10% off your entire order', 0, NULL, 0, 0.10, NULL, '2024-01-01', '2030-12-31'),
                ('F150SAVE', 'Save $1,000 on the Ford F-150', 1, 100, 1, NULL, 1000.00, '2024-01-01', '2030-12-31');
            """)

    conn.commit()

    cursor.close()
    conn.close()

    print("Database Populated")


def populateImages():
    """
    Scans the `productImages` folder for image files corresponding to inventory item names.
    Updates the `ItemImage` field in the Inventory table with binary image data (BLOB)
    for each matching item.
    
    Only processes files with extensions: .png, .jpg, .webp, .jfif
    The image filename (without extension) must match the `ItemName` in the database.
    """
    def resourcePath(relativePath):
        """
        Returns the absolute path to a resource file.

        Args:
            relativePath (str): Relative path to the resource.

        Returns:
            str: Absolute path to the resource file.
        """
        try:
            basePath = sys._MEIPASS
        except AttributeError:
            basePath = os.path.abspath(".")

        return os.path.join(basePath, relativePath)

    imageFolder = resourcePath("productImages")

    extensions = {".png", ".jpg", ".webp", ".jfif"}

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        for fileName in os.listdir(imageFolder):
            fileBase, ext = os.path.splitext(fileName)
            if ext.lower() not in extensions:
                continue

            filePath = os.path.join(imageFolder, fileName)
            with open(filePath, "rb") as f:
                imageData = f.read()

            cursor.execute("""
                    UPDATE Inventory
                    SET ItemImage = ?
                    WHERE LOWER(ItemName) = LOWER(?)
                """, (imageData, fileBase))

            conn.commit()
        print("Images successfully populated in Inventory table.")

    except Exception as e:
        print(f"Error in populateImages: {e}")

    finally:
        cursor.close()
        conn.close()