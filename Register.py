import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re
import DBLibrary as db
import Helper as h
import Login
import Help
import Manager

def registerPage(window, isManager, personID = None):
    """
    Displays the user registration page.

    Allows users or managers to register a new account. Dynamically builds and validates input fields,
    credentials, and security questions. Displays help, back, and submit buttons.

    Args:
        window (tk.Tk or tk.Frame): The main application window or container.
        isManager (bool): Whether the registration is being done by a manager.
        personID (int, optional): ID of the manager (if applicable). Defaults to None.
    """
    window.configure(background="#7393B3")

    # Main Frame
    mainFrame = ttk.Frame(window, padding="30 30 30 30")
    mainFrame.place(relx=0.44, rely=0.48, anchor="e")

    # Title
    titleLabel = ttk.Label(mainFrame, text="Create an Account", font=("Calibri", 24, "bold"))
    titleLabel.grid(column=0, row=0, columnspan=2, pady=(0, 20))

    # dictionary to store input fields key: name definition: object
    entries = {}

    # dictionary of personal info fields key: name definition: nullable
    infoFields = {
        "First Name": True,
        "Middle Name": False,
        "Last Name": True,
        "Title": False,
        "Suffix": False,
        "Address 1": True,
        "Address 2": False,
        "Address 3": False,
        "City": True,
        "State": True,
        "Zipcode": True,
        "Email": False,
        "Phone Primary": False,
        "Phone Secondary": False
    }

    # ensure input exists
    def validateInput():
        """
        Validates all form input fields for required data and formatting.

        Checks required personal information fields, credential fields, security questions,
        and applies format validation (e.g., for email, zip code, phone number, etc.).

        Returns:
            dict | bool: A dictionary of cleaned input values if valid, False otherwise.
        """
        missingFields = []
        data = {}
        for field, mandatory in infoFields.items():
            value = entries[field].get().strip()

            if mandatory and not value:
                missingFields.append(field)
            data[field] = value

        username = userInput.get()
        password = passInput.get()
        confirm_password = confirmPassInput.get()
        question1 = question1Input1.get().strip()
        question2 = question1Input2.get().strip()
        question3 = question1Input3.get().strip()
        question4 = question2Input1.get().strip()
        question5 = question2Input2.get().strip()
        question6 = question2Input3.get().strip()
        question7 = question3Input1.get().strip()
        question8 = question3Input2.get().strip()
        question9 = question3Input3.get().strip()

        if not username:
            missingFields.append("Username")
        if not password:
            missingFields.append("Password")
        if not confirm_password:
            missingFields.append("Confirm Password")

        if selected.get() == 1:
            if not question1:
                missingFields.append("What is your favorite Color?")
            if not question2:
                missingFields.append("Your favorite Toy's name?")
            if not question3:
                missingFields.append("Your Pet's name?")
        if selected.get() == 2:
            if not question4:
                missingFields.append("Your Home Town name?")
            if not question5:
                missingFields.append("Your mother's first name?")
            if not question6:
                missingFields.append("Your favorite Football Team?")
        if selected.get() == 3:
            if not question7:
                missingFields.append("What is your favorite food?")
            if not question8:
                missingFields.append("Favorite place to vacation?")
            if not question9:
                missingFields.append("Name of your favorite book?")

        if missingFields:
            messagebox.showerror(title="Missing Fields", message=f"Please fill in the following mandatory fields:\n{', '.join(missingFields)}")
            return False
        
        firstName = data["First Name"]
        middleName = data["Middle Name"]
        lastName = data["Last Name"]
        address1 = data["Address 1"]
        address2 = data["Address 2"]
        address3 = data["Address 3"]
        state = data["State"]
        zip = data["Zipcode"]
        email = data["Email"]
        phone1 = data["Phone Primary"]
        phone2 = data["Phone Secondary"]
        
        emailPattern = r"^(?!.*\.\.)[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,62}[a-zA-Z0-9]@[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*\.[a-zA-Z]{2,}$"
        zipPattern = r"^\d{5}(-\d{4})?$"
        statePattern = r"^(Al|Ak|Az|Ar|Ca|Co|Ct|De|Fl|Ga|Hi|Id|Il|In|Ia|Ks|Ky|La|Me|Md|Ma|Mi|Mn|Ms|Mo|Mt|Ne|Nv|Nh|Nj|Nm|Ny|Nc|Nd|Oh|Ok|Or|Pa|Ri|Sc|Sd|Tn|Tx|Ut|Vt|Va|Wa|Wv|Wi|Wy)$"
        phonePattern = r"^\d{10}"
        addressPattern = r"^[a-zA-Z0-9\s,.'-]+$"
        militaryPattern1 = r"^(CPR|OPC|PSC|UPR|UNIT)\s\d+(BOX\s\d{2,3})$"
        militaryPattern2 = r"^(APO|FPO)\s(AE|AP|AA)"
        boxPattern = r"^(P\.?O\.?\s*Box|Box)\s*\d+$"

        fNameValid = h.checkNames(firstName)
        if middleName:
            mNameValid = h.checkNames(middleName)
            if not mNameValid:
                messagebox.showerror(title="Invalid Name", message="Names can not contain special characters.")
                return False
        lNameValid = h.checkNames(lastName)

        if not fNameValid or not lNameValid:
            messagebox.showerror(title="Invalid Name", message="Names can not contain special characters.")
            return False

        if email and not re.match(emailPattern, email):
            messagebox.showerror(title="Invalid Email", message="Please enter a valid email address.")
            return False
        
        if not re.match(zipPattern, zip):
            messagebox.showerror(title="Invalid Zipcode", message="Please enter a valid zipcode (##### or #####-####).")
            return False
        
        if not re.match(statePattern, state):
            messagebox.showerror(title="Invalid State", message="Please enter a valid state - Capital then lowercase letter (Az).")
            return False
        
        if phone1 and not re.match(phonePattern, phone1):
            messagebox.showerror(title="Invalid Phone1", message="Please enter a valid format (##########).")
            return False
        if phone2 and not re.match(phonePattern, phone2):
            messagebox.showerror(title="Invalid Phone2", message="Please enter a valid format (##########).")
            return False
        
        if not re.match(addressPattern, address1):
            messagebox.showerror("Invalid Address1", "Please enter a valid Address 1.")
            return False
        if address2 and not re.match(addressPattern, address2) and not re.match(militaryPattern1, address2) and not re.match(militaryPattern2, address2) and not re.match(boxPattern, address2):
            messagebox.showerror("Invalid Address2", "Please enter a valid Address 2.")
            return False
        if address3 and not re.match(addressPattern, address3) and not re.match(militaryPattern1, address3) and not re.match(militaryPattern2, address3) and not re.match(boxPattern, address3):
            messagebox.showerror("Invalid Address3", "Please enter a valid Address 3.")
            return False
        
        return data
    
    def submit():
        """
        Submits the registration form after validating input.

        Collects and maps answers to selected security questions,
        validates username and password using helper functions,
        and inserts the user into the database. Displays a message upon success.
        """
        data = validateInput()
        if data:
            position = positionVar.get()
            positionID = 1 if position == "customer" else 2

            print("good data")
            goodUser = h.checkUsername(userInput.get(), userInput)
            goodPass = h.checkPassword(passInput.get(), confirmPassInput.get(), passInput, confirmPassInput)
            print("User: ", goodUser, "Pass: ", goodPass)
            if goodUser and goodPass:
                print("good user and pass")
                data["Username"] = userInput.get()
                data["Password"] = passInput.get()
                data["SelectedSet"] = selected.get()
                if selected.get() == 1:
                    print("selected = 1")
                    data["Question1"], data["Answer1"] = question1Label1.cget("text"), question1Input1.get().strip()
                    data["Question2"], data["Answer2"] = question1Label2.cget("text"), question1Input2.get().strip()
                    data["Question3"], data["Answer3"] = question1Label3.cget("text"), question1Input3.get().strip()
                elif selected.get() == 2:
                    data["Question4"], data["Answer4"] = question2Label1.cget("text"), question2Input1.get().strip()
                    data["Question5"], data["Answer5"] = question2Label2.cget("text"), question2Input2.get().strip()
                    data["Question6"], data["Answer6"] = question2Label3.cget("text"), question2Input3.get().strip()
                elif selected.get() == 3:
                    data["Question7"], data["Answer7"] = question3Label1.cget("text"), question3Input1.get().strip()
                    data["Question8"], data["Answer8"] = question3Label2.cget("text"), question3Input2.get().strip()
                    data["Question9"], data["Answer9"] = question3Label3.cget("text"), question3Input3.get().strip()
                
                success = db.registerUser(data, positionID)
                if success:
                    print("Success")
                    h.clearAllInputs(mainFrame)
                    h.clearAllInputs(credFrame)
                    h.clearAllInputs(frame1)
                    h.clearAllInputs(frame2)
                    h.clearAllInputs(frame3)
                    messagebox.showinfo(title="Success", message="User registration completed!")
    
    def back():
        """
        Returns the user to the appropriate previous screen.

        If the registration was opened by a manager, it returns to the manager page;
        otherwise, it returns to the login page.
        """
        h.clearScreen(window)
        if isManager:
            Manager.managerPage(window, personID)
        else:
            Login.loginPage(window)

    # create labels and input fields
    row = 1
    for field in infoFields:
        label = ttk.Label(mainFrame, text=f"{field}: {'*' if infoFields[field] else ''}")
        label.grid(row=row, column=0, sticky="E", pady=5, padx=5)

        entry = ttk.Entry(mainFrame, width=30)
        entry.grid(row=row, column=1, sticky="W", pady=5, padx=5)
        entries[field] = entry
        row += 1

    # User Credentials Frame
    credFrame = ttk.Frame(window, padding="30 30 30 30")
    credFrame.place(relx=0.45, rely=0.4, anchor="w")

    # Username
    userLabel = ttk.Label(credFrame, text="Username")
    userLabel.grid(column=0, row=1, sticky="W", pady=5)

    userInput = ttk.Entry(credFrame, width=25)
    userInput.grid(column=1, row=1, pady=5)

    # Password
    passLabel = ttk.Label(credFrame, text="Password")
    passLabel.grid(column=0, row=2, sticky="W", pady=5)

    passInput = ttk.Entry(credFrame, width=25)
    passInput.grid(column=1, row=2, pady=5)

    # Confirm Password
    confirmPassLabel = ttk.Label(credFrame, text="Confirm Password")
    confirmPassLabel.grid(column=0, row=3, sticky="W", pady=5)

    confirmPassInput = ttk.Entry(credFrame, width=25)
    confirmPassInput.grid(column=1, row=3, pady=5)

    # Security Questions
    questionLabel = ttk.Label(credFrame, text="Security Questions:")
    questionLabel.grid(column=0, row=4)

    def toggleButtons():
        """
        Activates the appropriate set of security question input fields based on the selected radio button.
        Disables the other two sets of questions.
        """
        if selected.get() == 1:
            h.setFrame(frame1, "normal")
            h.setFrame(frame2, "disabled")
            h.setFrame(frame3, "disabled")
        elif selected.get() == 2:
            h.setFrame(frame1, "disabled")
            h.setFrame(frame2, "normal")
            h.setFrame(frame3, "disabled")
        elif selected.get() == 3:
            h.setFrame(frame1, "disabled")
            h.setFrame(frame2, "disabled")
            h.setFrame(frame3, "normal")


    # radio buttons
    selected = tk.IntVar(value=1)

    rButton1 = ttk.Radiobutton(credFrame, variable=selected, value=1, command=toggleButtons)
    rButton1.grid(column=0, row=5, sticky='w', padx=0, pady=0)


    rButton2 = ttk.Radiobutton(credFrame, variable=selected, value=2, command=toggleButtons)
    rButton2.grid(column=0, row=6, sticky='w', padx=0, pady=0)

    rButton3 = ttk.Radiobutton(credFrame, variable=selected, value=3, command=toggleButtons)
    rButton3.grid(column=0, row=7, sticky='w', padx=0, pady=0)

    # labels and inputs frames
    frame1 = ttk.Frame(credFrame)
    frame1.grid(column=1, row=5)

    frame2 = ttk.Frame(credFrame)
    frame2.grid(column=1, row=6)

    frame3 = ttk.Frame(credFrame)
    frame3.grid(column=1, row=7)
    
    # question labels
    question1Label1 = ttk.Label(frame1, text="What is your favorite Color?")
    question1Label1.grid(column=0, row=0, sticky='w', padx=0, pady=0)
    question1Label2 = ttk.Label(frame1, text="Your favorite Toy's name?")
    question1Label2.grid(column=0, row=1, sticky='w', padx=0, pady=0)
    question1Label3 = ttk.Label(frame1, text="Your Pet's name?")
    question1Label3.grid(column=0, row=2, sticky='w', padx=0, pady=0)

    question2Label1 = ttk.Label(frame2, text="Your Home Town name?")
    question2Label1.grid(column=0, row=0, sticky='w', padx=0, pady=0)
    question2Label2 = ttk.Label(frame2, text="Your mother's first name?")
    question2Label2.grid(column=0, row=1, sticky='w', padx=0, pady=0)
    question2Label3 = ttk.Label(frame2, text="Your favorite Football Team?")
    question2Label3.grid(column=0, row=2, sticky='w', padx=0, pady=0)

    question3Label1 = ttk.Label(frame3, text="What is your favorite food?")
    question3Label1.grid(column=0, row=0, sticky='w', padx=0, pady=0)
    question3Label2 = ttk.Label(frame3, text="Favorite place to vacation?")
    question3Label2.grid(column=0, row=1, sticky='w', padx=0, pady=0)
    question3Label3 = ttk.Label(frame3, text="Name of your favorite book?")
    question3Label3.grid(column=0, row=2, sticky='w', padx=0, pady=0)

    # question Input Fields
    question1Input1 = ttk.Entry(frame1, width=25)
    question1Input1.grid(column=1, row=0, sticky='w', padx=0, pady=5)
    question1Input2 = ttk.Entry(frame1, width=25)
    question1Input2.grid(column=1, row=1, sticky='w', padx=0, pady=5)
    question1Input3 = ttk.Entry(frame1, width=25)
    question1Input3.grid(column=1, row=2, sticky='w', padx=0, pady=5)

    question2Input1 = ttk.Entry(frame2, width=25)
    question2Input1.grid(column=1, row=0, sticky='w', padx=0, pady=5)
    question2Input2 = ttk.Entry(frame2, width=25)
    question2Input2.grid(column=1, row=1, sticky='w', padx=0, pady=5)
    question2Input3 = ttk.Entry(frame2, width=25)
    question2Input3.grid(column=1, row=2, sticky='w', padx=0, pady=5)

    question3Input1 = ttk.Entry(frame3, width=25)
    question3Input1.grid(column=1, row=0, sticky='w', padx=0, pady=5)
    question3Input2 = ttk.Entry(frame3, width=25)
    question3Input2.grid(column=1, row=1, sticky='w', padx=0, pady=5)
    question3Input3 = ttk.Entry(frame3, width=25)
    question3Input3.grid(column=1, row=2, sticky='w', padx=0, pady=5)

    toggleButtons()

    passInstructions = ttk.Label(window, text="""Password must be between 8 and 20 characters and must contain at least 3 of the following:
                                 \n- (1) uppercase letter\n- (1) lower case letter\n- (1) number\n- (1) special character
                                 \npassword may not contain spaces""", background="#7393B3")
    passInstructions.place(relx=0.69, rely=0.9, anchor="s")

    # If manager is creating the account, show a Position dropdown
    if isManager:
        positionLabel = ttk.Label(window, text="Position *")
        positionLabel.place(relx=.8, rely=0.8, anchor="s")

        positionVar = tk.StringVar()
        positionDropdown = ttk.OptionMenu(window, positionVar, "customer", "customer", "manager")
        positionDropdown.place(relx=.8, rely=0.8, anchor="s")
    else:
        # Default to Customer
        positionVar = tk.StringVar(value="customer")

    submitButton = ttk.Button(window, text="Submit", command=submit)
    submitButton.place(relx=0.9, rely=0.95, anchor="s")

    backButton = ttk.Button(window, text="Back", command=back)
    backButton.place(relx=0.8, rely=0.95, anchor="s")

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("Register") if not isManager else Help.helpPage("RegisterManager"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")