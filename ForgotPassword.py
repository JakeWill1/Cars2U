import tkinter as tk
from tkinter import ttk, messagebox
import DBLibrary as db
import Login
import Helper as h
import Help

def forgotPasswordPage(window, username):
    """
    Displays the Forgot Password page where users can answer their security 
    questions and set a new password if the answers are correct.

    Args:
        window (tk.Tk): The main application window.
        username (str): The username of the account attempting password recovery.
    """
    window.configure(background="#7393B3")

    # title
    title = ttk.Label(window, text="Change Password", font=("Calibri", 48, "bold"), background="#7393B3")
    title.place(relx=0.5, rely=0.15, anchor="center")

    userLabel = ttk.Label(window, text=f"User: {username}", font=("Calibri", 24, "bold"), background="#7393B3")
    userLabel.place(relx=0.5, rely=0.25, anchor="center")

    def loadSecurityQuestions():
        """
        Loads the security questions and correct answers for the given username 
        from the database and populates the corresponding labels.
        """
        securityData = db.loadQuestions(username)
        
        question1Label.config(text=securityData[0])
        question2Label.config(text=securityData[1])
        question3Label.config(text=securityData[2])

        global correctAnswers
        correctAnswers = [securityData[3].lower(), securityData[4].lower(), securityData[5].lower()]

    def verifyAnswers():
        """
        Checks whether the user's input answers match the correct answers 
        stored in the database.

        Returns:
            bool: True if all answers match, False otherwise.
        """
        inputAnswers = [
            answer1Input.get().strip().lower(),
            answer2Input.get().strip().lower(),
            answer3Input.get().strip().lower()
        ]

        if inputAnswers == correctAnswers:
            return True
        else:
            h.clearAllInputs(frame)
            messagebox.showerror(title="Error", message="Incorrect answers. Please try again.")
            return False
        
    def submit():
        """
        Verifies the user's answers to security questions and attempts to update 
        the password if the answers are correct and the new password meets all requirements.
        """
        correct = verifyAnswers()
        if correct:
            password = newPassInput.get()
            confirmPassword = confirmPassInput.get()
            goodPass = h.checkPassword(password, confirmPassword, newPassInput, confirmPassInput)
            if goodPass:
                db.changePassword(username, password)
                h.clearAllInputs(frame)
        
    def back():
        """
        Returns the user to the login page.
        """
        h.clearScreen(window)
        Login.loginPage(window)

    # main frame
    frame = ttk.Frame(window, padding="30 30 30 30")
    frame.place(relx=0.5, rely=0.45, anchor="center")

    # gui widgets
    question1Label = ttk.Label(frame, text="Security Question 1:")
    question1Label.grid(column=0, row=1, padx=5, pady=5)
    answer1Input = ttk.Entry(frame, width=30)
    answer1Input.grid(column=1, row=1, padx=5, pady=5)

    question2Label = ttk.Label(frame, text="Security Question 2:")
    question2Label.grid(column=0, row=2, padx=5, pady=5)
    answer2Input = ttk.Entry(frame, width=30)
    answer2Input.grid(column=1, row=2, padx=5, pady=5)

    question3Label = ttk.Label(frame, text="Security Question 3:")
    question3Label.grid(column=0, row=3, padx=5, pady=5)
    answer3Input = ttk.Entry(frame, width=30)
    answer3Input.grid(column=1, row=3, padx=5, pady=5)

    newPassLabel = ttk.Label(frame, text="New Password:")
    newPassLabel.grid(column=0, row=4, padx=5, pady=5)
    newPassInput = ttk.Entry(frame, width=30)
    newPassInput.grid(column=1, row=4, padx=5, pady=5)

    confirmPassLabel = ttk.Label(frame, text="Confirm New Password:")
    confirmPassLabel.grid(column=0, row=5, padx=5, pady=5)
    confirmPassInput = ttk.Entry(frame, width=30)
    confirmPassInput.grid(column=1, row=5, padx=5, pady=5)

    passInstructions = ttk.Label(window, text="""Password must be between 8 and 20 characters and must contain at least 3 of the following:
                                 \n- (1) uppercase letter\n- (1) lower case letter\n- (1) number\n- (1) special character
                                 \npassword may not contain spaces""", background="#7393B3")
    passInstructions.place(relx=0.5, rely=0.75, anchor="center")

    submitButton = ttk.Button(window, text="Submit", command=submit)
    submitButton.place(relx=0.45, rely=0.9, anchor="center")

    backButton = ttk.Button(window, text="Back", command=back)
    backButton.place(relx=0.55, rely=0.9, anchor="center")

    helpButton = ttk.Button(window, text="Help", command=lambda: Help.helpPage("Forgot Password"))
    helpButton.place(relx=0.05, rely=0.95, anchor="sw")

    loadSecurityQuestions()