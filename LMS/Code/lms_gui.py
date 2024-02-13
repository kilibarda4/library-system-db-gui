import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
from ttkbootstrap import constants
import ttkbootstrap as tb
from tkinter import messagebox
import sqlite3
import datetime
import locale


# Connect to the SQLite
conn = sqlite3.connect("LMS.sql")
cursor = conn.cursor()


class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1200x900")
        self.style = Style(theme="cyborg")

        self.main_frame = ttk.Frame(
            self.root, padding="20", width=600, height=800)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Stack to keep track of pages
        self.page_stack = []

        self.selected_item = None
        self.book_id = None
        self.branch_id = None

        self.tb = tb
        self.start_date = None
        self.end_date = None

        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

        # Main Page
        self.create_main_page()

    def create_main_page(self):
        self.clear_main_frame()

        ttk.Label(self.main_frame, text="Welcome to LMS",
                  style="h1.TLabel").pack(pady=20)

        user_button = ttk.Button(self.main_frame, text="User",
                                 style="success.TButton", width=20, command=self.show_user_page)
        admin_button = ttk.Button(self.main_frame, text="Admin",
                                  style="info.TButton", width=20, command=self.show_admin_page)

        user_button.pack(pady=10)
        admin_button.pack(pady=10)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_user_page(self):
        self.page_stack.append(self.create_main_page)
        self.clear_main_frame()

        ttk.Label(self.main_frame, text="User Page",
                  style="h1.TLabel").pack(pady=20)

        checkout_button = ttk.Button(self.main_frame, text="Checkout Books",
                                     style="success.TButton", width=20, command=self.checkout_books)
        return_button = ttk.Button(self.main_frame, text="Return Books",
                                   style="info.TButton", width=20, command=self.return_books)
        back_button = ttk.Button(self.main_frame, text="Back",
                                 style="warning.TButton", width=20, command=self.back_to_main_page)

        checkout_button.pack(pady=10)
        return_button.pack(pady=10)
        back_button.pack(pady=10)

    def checkout_books(self):
        query_books = "SELECT B.Book_Id, B.Title, B.Publisher_name, BC.Branch_Id " \
            "FROM BOOK B " \
            "JOIN BOOK_COPIES BC ON B.Book_Id = BC.Book_Id"
        cursor.execute(query_books)
        books_data = cursor.fetchall()
        print("Available Books:")
        for row in books_data:
            print(row)

        self.clear_main_frame()
        ttk.Label(self.main_frame, text="Available Books",
                  style="h1.TLabel").pack(pady=20)

        tree = ttk.Treeview(self.main_frame, columns=list(
            range(len(books_data[0]))), show="headings", height=len(books_data))

        # column headings
        headings = ["Book ID", "Title", "Publisher Name", "Branch ID"]
        for i, heading in enumerate(headings):
            tree.heading(i, text=heading)
            tree.column(i, width=250)

        for row in books_data:
            tree.insert("", "end", values=row)

        tree.pack(pady=10, padx=10)

        checkout_button = ttk.Button(self.main_frame, text="Check Out Book",
                                     style="success.TButton", width=20, command=lambda: self.checkout_selected_book(tree))
        checkout_button.pack(pady=10)

        back_button = ttk.Button(self.main_frame, text="Back",
                                 style="warning.TButton", width=20, command=self.back_to_user_page)
        back_button.pack(pady=10)

    def checkout_selected_book(self, tree):
        selected_item = tree.selection()
        if selected_item:

            self.selected_item = selected_item

            selected_values = tree.item(selected_item, "values")
            book_id = selected_values[0]

            # Branch ids of all branches that have the selected book available
            query_branch_id = f"SELECT Branch_Id FROM BOOK_COPIES WHERE Book_Id = {book_id} AND No_Of_Copies > 0"
            cursor.execute(query_branch_id)
            result = cursor.fetchall()

            self.branch_id = [row[0] for row in result]

            if not self.branch_id:
                print(f"Book ID {book_id} is temporarily unavailable.")
                messagebox.showinfo(
                    "Checkout Error", f"Book ID {book_id} is temporarily unavailable. Please select another book")
                self.back_to_user_page()
            else:
                self.user_verification(book_id, self.branch_id[0])
        else:
            print("No book selected. Please select a book to check out.")

    def return_books(self):
        # Implement Return Books
        pass

    def user_verification(self, book_id, branch_id):
        self.page_stack.append(self.create_main_page)
        self.clear_main_frame()

        ttk.Label(self.main_frame, text="Login",
                  style="h1.TLabel").pack(pady=20)

        card_no_entry = ttk.Entry(
            self.main_frame, style="info.TEntry", font=('Arial', 12))

        ttk.Label(self.main_frame, text="Card Number:",
                  style="h2.TLabel").pack(pady=10)
        card_no_entry.pack(pady=5)

        login_button = ttk.Button(
            self.main_frame, text="Login", style="success.TButton", width=20, command=lambda: self.user_verification_cmd(card_no_entry.get(), book_id, branch_id))
        back_button = ttk.Button(self.main_frame, text="Back",
                                 style="warning.TButton", width=20, command=self.back_to_user_page)

        login_button.pack(pady=10)
        back_button.pack(pady=10)

    def user_verification_cmd(self, card_no, book_id, branch_id):
        if not card_no:
            messagebox.showwarning(
                "Incomplete Information", "Please fill in card information.")
            return

        query_get_card_no = f"SELECT * FROM BORROWER WHERE Card_No = '{card_no}'"
        cursor.execute(query_get_card_no)
        card_no_result = cursor.fetchone()

        if card_no_result is not None:
            name = card_no_result[1]
            due_date = datetime.date.today() + datetime.timedelta(days=15)
            query_checkout_book = f"INSERT INTO BOOK_LOANS (Book_Id, Branch_Id, Card_No, Date_Out, Due_Date, Returned_date) " \
                f"VALUES ('{book_id}', '{branch_id}', '{card_no}', CURRENT_DATE, '{due_date}', 'Null')"
            cursor.execute(query_checkout_book)
            conn.commit()
            messagebox.showinfo("Success!",
                                f"Thank you {name}, your book is due on {due_date}!")
        else:
            messagebox.showinfo("Login Failed",
                                "Card number not found. Please sign up before proceeding.")
            self.add_borrower()

    def show_admin_page(self):
        self.page_stack.append(self.create_main_page)
        self.clear_main_frame()

        ttk.Label(self.main_frame, text="Admin Page",
                  style="h1.TLabel").pack(pady=20)

        add_books_button = ttk.Button(
            self.main_frame, text="Add Books", style="success.TButton", width=20, command=self.add_books)
        add_borrower_button = ttk.Button(
            self.main_frame, text="Add Borrower", style="success.TButton", width=20, command=self.add_borrower)
        view_inventory_button = ttk.Button(
            self.main_frame, text="View Inventory", style="info.TButton", width=20, command=self.view_inventory)
        view_vborrower_button = ttk.Button(
            self.main_frame, text="View Borrower Info", style="info.TButton", width=20, command=self.set_bfilters)
        view_book_loan_info_button = ttk.Button(
            self.main_frame, text="View Book Loan Info", style="info.TButton", width=20, command=self.set_book_filters) #filter view by book
        view_loans_button = ttk.Button(
            self.main_frame, text="Search Loans By Title", style="warning.TButton", width=20, command=self.search_loans_title)
        view_late_days_button = ttk.Button(
            self.main_frame, text="Late Books by Date", style="warning.TButton", width=20, command=self.late_days_range)
        back_button = ttk.Button(self.main_frame, text="Back",
                                 style="danger.TButton", width=20, command=self.back_to_main_page)

        add_books_button.pack(pady=10)
        add_borrower_button.pack(pady=10)
        view_inventory_button.pack(pady=10)
        view_vborrower_button.pack(pady=10)
        view_book_loan_info_button.pack(pady=10)
        view_loans_button.pack(pady=10)
        view_late_days_button.pack(pady=10)
        back_button.pack(pady=10)

    def add_books(self):
        self.page_stack.append(self.create_main_page)
        self.clear_main_frame()

        ttk.Label(self.main_frame, text="Add Book",
                  style="h1.TLabel").pack(pady=20)

        book_entry = ttk.Entry(
            self.main_frame, style="info.TEntry", font=('Arial', 12))
        pub_entry = ttk.Entry(
            self.main_frame, style="info.TEntry", font=('Arial', 12))
        author_entry = ttk.Entry(
            self.main_frame, style="info.TEntry", font=('Arial', 12))

        ttk.Label(self.main_frame, text="Book Title:",
                  style="h2.TLabel").pack(pady=10)
        book_entry.pack(pady=5)

        ttk.Label(self.main_frame, text="Publisher Name:",
                  style="h2.TLabel").pack(pady=10)
        pub_entry.pack(pady=5)

        ttk.Label(self.main_frame, text="Author Name:",
                  style="h2.TLabel").pack(pady=10)
        author_entry.pack(pady=5)

        add_book_button = ttk.Button(
            self.main_frame, text="Add Book", style="success.TButton", width=20, command=lambda: self.add_books_cmd(book_entry.get(), pub_entry.get(), author_entry.get()))
        back_button = ttk.Button(self.main_frame, text="Back",
                                 style="warning.TButton", width=20, command=self.show_admin_page)

        add_book_button.pack(pady=10)
        back_button.pack(pady=10)

    def add_books_cmd(self, book, pub, author):
        if not book or not pub or not author:
            messagebox.showwarning(
                "Incomplete Information", "Please fill in all the fields.")
            return

        # Check if book already exists
        query_check_book = f"SELECT Book_Id FROM BOOK WHERE Title = '{book}' AND Publisher_name = '{pub}'"
        cursor.execute(query_check_book)
        book_exists = cursor.fetchone()

        if not book_exists:
            query_add_into_book = f"INSERT INTO BOOK (Title, Publisher_name) VALUES ('{book}', '{pub}')"
            cursor.execute(query_add_into_book)
            conn.commit()

        # Check if author already exists for the book
        query_check_author = f"SELECT * FROM BOOK_AUTHORS WHERE Book_Id = (SELECT Book_Id FROM BOOK WHERE Title = '{book}' AND Publisher_name = '{pub}')"
        cursor.execute(query_check_author)
        author_exists = cursor.fetchone()

        if not author_exists:
            # Add author into book authors table
            query_add_into_auth = f"INSERT INTO BOOK_AUTHORS VALUES " \
                f"((SELECT Book_Id FROM BOOK WHERE Title = '{book}' AND Publisher_name = '{pub}'), '{author}')"
            cursor.execute(query_add_into_auth)
            conn.commit()

        query_get_branches = "SELECT Branch_Id FROM LIBRARY_BRANCH"
        cursor.execute(query_get_branches)
        result = cursor.fetchall()
        branches = [row[0] for row in result]

        for x in branches:
            # Check if book copies already exist for the branch
            query_check_book_copies = f"SELECT No_Of_Copies FROM BOOK_COPIES " \
                f"WHERE Book_Id = (SELECT Book_Id FROM BOOK WHERE Title = '{book}' AND Publisher_name = '{pub}') " \
                f"AND Branch_Id = '{x}'"
            cursor.execute(query_check_book_copies)
            book_copies_exist = cursor.fetchone()

            if book_copies_exist:
                # Update book copies
                query_update_books = f"UPDATE BOOK_COPIES SET No_Of_Copies = No_Of_Copies + 5 " \
                    f"WHERE Book_Id = (SELECT Book_Id FROM BOOK WHERE Title = '{book}' " \
                    f"AND Publisher_name = '{pub}') AND Branch_Id = {x}"
            else:
                # Insert book copies
                query_update_books = f"INSERT INTO BOOK_COPIES VALUES ((SELECT Book_Id FROM BOOK WHERE Title = '{book}' " \
                    f"AND Publisher_name = '{pub}'), {x}, 5)"

            cursor.execute(query_update_books)
            conn.commit()

        messagebox.showinfo("Book Addition Successful",
                            "Book addition successful.")

    def view_inventory(self):
        query_inventory = "SELECT B.Book_Id, B.Title, BC.Branch_Id, BC.No_Of_Copies " \
            "FROM BOOK B " \
            "JOIN BOOK_COPIES BC ON B.Book_Id = BC.Book_Id"
        cursor.execute(query_inventory)
        inventory_data = cursor.fetchall()
        print("Current Inventory:")
        for row in inventory_data:
            print(row)

        self.clear_main_frame()
        ttk.Label(self.main_frame, text="Current Inventory",
                  style="h1.TLabel").pack(pady=20)

        tree = ttk.Treeview(self.main_frame, columns=list(
            range(len(inventory_data[0]))), show="headings", height=len(inventory_data))

        # column headings
        headings = ["Book ID", "Title", "Branch ID", "Number of Copies"]
        for i, heading in enumerate(headings):
            tree.heading(i, text=heading)
            tree.column(i, width=250)

        for row in inventory_data:
            tree.insert("", "end", values=row)

        tree.pack(pady=10, padx=10)

        back_button = ttk.Button(self.main_frame, text="Back",
                                 style="warning.TButton", width=20, command=self.show_admin_page)
        back_button.pack(pady=10)

    def set_bfilters(self):
        self.page_stack.append(self.create_main_page)
        self.clear_main_frame()

        ttk.Label(self.main_frame, text="Set Borrower Filters",
                  style="h1.TLabel").pack(pady=20)

        card_entry = ttk.Entry(
            self.main_frame, style="info.TEntry", font=('Arial', 12))
        name_entry = ttk.Entry(
            self.main_frame, style="info.TEntry", font=('Arial', 12))

        ttk.Label(self.main_frame, text="Card Number:",
                  style="h2.TLabel").pack(pady=10)
        card_entry.pack(pady=5)

        ttk.Label(self.main_frame, text="Name/Part of Name:",
                  style="h2.TLabel").pack(pady=10)
        name_entry.pack(pady=5)

        show_view_button = ttk.Button(
            self.main_frame, text="Show Borrower Info", style="success.TButton", width=20, command=lambda: self.view_borrower_info(card_entry.get(), name_entry.get()))
        back_button = ttk.Button(self.main_frame, text="Back",
                                 style="warning.TButton", width=20, command=self.show_admin_page)

        show_view_button.pack(pady=10)
        back_button.pack(pady=10)

    def view_borrower_info(self, card, name):
        
        #update view
        self.view_loans()

        if card and not name:
            query_view_bor = f"SELECT DISTINCT Card_No, Borrower_Name, ROUND(SUM(LateFeeBalance), 2) FROM vBookLoanInfo WHERE Card_No = {card} GROUP BY Card_No ORDER BY LateFeeBalance;"
            cursor.execute(query_view_bor)
            borrower_data = cursor.fetchall()
        elif name and not card:
            query_view_bor = f"SELECT DISTINCT Card_No, Borrower_Name, ROUND(SUM(LateFeeBalance), 2) FROM vBookLoanInfo WHERE Borrower_Name LIKE '%{name}%' GROUP BY Card_No ORDER BY LateFeeBalance;"
            cursor.execute(query_view_bor)
            borrower_data = cursor.fetchall()
        elif name and card:
            query_view_bor = f"SELECT DISTINCT Card_No, Borrower_Name, ROUND(SUM(LateFeeBalance), 2) FROM vBookLoanInfo WHERE Card_No = {card} AND Borrower_Name LIKE '%{name}%' GROUP BY Card_No ORDER BY LateFeeBalance;"
            cursor.execute(query_view_bor)
            borrower_data = cursor.fetchall()
        else:
            query_view_bor = f"SELECT DISTINCT Card_No, Borrower_Name, ROUND(SUM(LateFeeBalance), 2) FROM vBookLoanInfo GROUP BY Card_No ORDER BY LateFeeBalance ASC;"
            cursor.execute(query_view_bor)
            borrower_data = cursor.fetchall()

        print("Borrower Information:")
        if borrower_data:
            for row in borrower_data:
                print(row)
            self.clear_main_frame()
            ttk.Label(self.main_frame, text="Borrower Information",
                    style="h1.TLabel").pack(pady=20)

            tree = ttk.Treeview(self.main_frame, columns=list(
                range(len(borrower_data[0]))), show="headings", height=len(borrower_data))

            # Add column headings
            headings = ["Card No.", "Borrower Name", "Late Fee Balance"]
            for i, heading in enumerate(headings):
                tree.heading(i, text=heading)
                tree.column(i, width=150)  # Adjust width as needed

            # Add data to the treeview
            for row in borrower_data:
                tree.insert("", "end", values=(row[0], row[1], 'Non-Applicable' if row[2] is None else f'${row[2]:.2f}'))

            tree.pack(pady=10, padx=10)
        else:
            self.page_stack.append(self.create_main_page)
            self.clear_main_frame()
            ttk.Label(self.main_frame, text="Borrower Information:",
                  style="h1.TLabel").pack(pady=20)
            ttk.Label(self.main_frame, text="No results found",
                      style="h2.TLabel").pack(pady=20)

        back_button = ttk.Button(self.main_frame, text="Back",
                                 style="warning.TButton", width=20, command=self.show_admin_page)
        back_button.pack(pady=10)

    def set_book_filters(self):
        self.page_stack.append(self.create_main_page)
        self.clear_main_frame()

        ttk.Label(self.main_frame, text="Set Book Filters",
                  style="h1.TLabel").pack(pady=20)

        card_entry = ttk.Entry(
            self.main_frame, style="info.TEntry", font=('Arial', 12))
        book_id_entry = ttk.Entry(
            self.main_frame, style="info.TEntry", font=('Arial', 12))
        book_title_entry = ttk.Entry(
            self.main_frame, style="info.TEntry", font=('Arial', 12))

        ttk.Label(self.main_frame, text="*Card Number:",
                  style="h2.TLabel").pack(pady=10)
        card_entry.pack(pady=5)

        ttk.Label(self.main_frame, text="Book Id:",
                  style="h2.TLabel").pack(pady=10)
        book_id_entry.pack(pady=5)

        ttk.Label(self.main_frame, text="Book Title/Part of Title:",
                  style="h2.TLabel").pack(pady=10)
        book_title_entry.pack(pady=5)

        show_view_button = ttk.Button(
            self.main_frame, text="Show Book Info", style="success.TButton", width=20, command=lambda: self.view_book_loan_info(card_entry.get(), book_id_entry.get(), book_title_entry.get()))
        back_button = ttk.Button(self.main_frame, text="Back",
                                 style="warning.TButton", width=20, command=self.show_admin_page)

        show_view_button.pack(pady=10)
        back_button.pack(pady=10)

    def view_book_loan_info(self, card, book_id, title):
        if not card:
            messagebox.showwarning("Missing Card Number", "Please enter a card number to search.")
            return
        
        #update view
        self.view_loans()

        if not book_id and not title:
            query_no_filters = f"SELECT Book_Title, Date_Out, Due_Date, Returned_date, TotalDays, Days_Late, LateFeeBalance, Branch_Id FROM vBookLoanInfo WHERE Card_No = {card} ORDER BY LateFeeBalance DESC"
            cursor.execute(query_no_filters)
            book_loan_data = cursor.fetchall()
        elif book_id and not title:
            query_book_id = f"SELECT Book_Title, Date_Out, Due_Date, Returned_date, TotalDays, Days_Late, LateFeeBalance, Branch_Id FROM vBookLoanInfo WHERE Card_No = {card} AND Book_Id = {book_id}"
            cursor.execute(query_book_id)
            book_loan_data = cursor.fetchall()
        elif title and not book_id:
            query_title = f"SELECT Book_Title, Date_Out, Due_Date, Returned_date, TotalDays, Days_Late, LateFeeBalance, Branch_Id FROM vBookLoanInfo WHERE Card_No = {card} AND Book_Title LIKE '%{title}%'"
            cursor.execute(query_title)
            book_loan_data = cursor.fetchall()
        else:
            query_both = f"SELECT Book_Title, Date_Out, Due_Date, Returned_date, TotalDays, Days_Late, LateFeeBalance, Branch_Id FROM vBookLoanInfo WHERE Card_No = {card} AND Book_Id = {book_id} AND Book_Title LIKE '%{title}%'"
            cursor.execute(query_both)
            book_loan_data = cursor.fetchall()

        if not book_loan_data:
            messagebox.showinfo("No Results Found", "No results found. Please try again.")
            return

        print("Book Loan Information:")
        for row in book_loan_data:
            print(row)
        self.clear_main_frame()
        ttk.Label(self.main_frame, text="Book Loan Information",
                  style="h1.TLabel").pack(pady=20)

        tree = ttk.Treeview(self.main_frame, columns=list(
            range(len(book_loan_data[0]))), show="headings", height=len(book_loan_data))

        headings = ["Title", "Date Out",
                    "Due Date", "Returned Date", "Days Loaned Out", "Days Late", "Late Fee Balance", "Branch ID"]
        for i, heading in enumerate(headings, start=1):
            tree.heading(f'#{i}', text=heading, anchor='w')
            tree.column(f'#{i}', width=150, anchor='w') 

        for row in book_loan_data:
            tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[5], 'Non-Applicable' if row[6] == '0.00' else f'${row[6]}', row[7]))
        headings = ["Title", "Date Out",
                    "Due Date", "Returned Date", "Days Loaned Out", "Days Late", "Late Fee Balance", "Branch ID"]
        for i, heading in enumerate(headings, start=1):
            tree.heading(f'#{i}', text=heading, anchor='w')
            tree.column(f'#{i}', width=150, anchor='w') 

        tree.pack(pady=10, padx=10)

        back_button = ttk.Button(self.main_frame, text="Back",
                                 style="warning.TButton", width=20, command=self.show_admin_page)
        back_button.pack(pady=10)

    # create view for book loan info
    def view_loans(self):

        drop_view_querry = "DROP VIEW IF EXISTS vBookLoanInfo"
        cursor.execute(drop_view_querry)
        conn.commit()

        create_view_querry = """
        CREATE VIEW vBookLoanInfo AS
        SELECT 
        Card_No, 
        Name as Borrower_Name, 
        Date_Out,
        Due_Date,
        Returned_date,
        (CASE WHEN Returned_date = 'Null' THEN CAST(julianday('now') - julianday(Date_out) AS INTEGER)
              WHEN Returned_date = 'NULL' THEN CAST(julianday('now') - julianday(Date_out) AS INTEGER)
              WHEN Returned_date IS NULL THEN CAST(julianday('now') - julianday(Date_out) AS INTEGER)
              ELSE CAST(julianday(Returned_date) - julianday(Date_out) AS INTEGER) END) as TotalDays,
       Title as Book_Title, 
       (CASE WHEN julianday(Returned_date) - julianday(Due_Date) > 0 THEN (julianday(Returned_date) - julianday(Due_Date))
             WHEN Returned_date = 'NULL' AND (julianday('now') - julianday(Due_Date) > 0) THEN ROUND(julianday('now') - julianday(Due_Date), 0)
             WHEN Returned_date = 'Null' AND (julianday('now') - julianday(Due_Date) > 0) THEN ROUND(julianday('now') - julianday(Due_Date), 0)
            ELSE 0 END) as Days_Late,
       Branch_Id, 
       (CASE WHEN julianday(Returned_date) - julianday(Due_Date) > 0 THEN printf("%.2f",((julianday(Returned_date) - julianday(Due_Date)) * LateFee))
             WHEN Returned_date = 'NULL' AND (julianday('now') - julianday(Due_Date) > 0) THEN printf("%.2f",((ROUND(julianday('now') - julianday(Due_Date), 2) * LateFee)))
             WHEN Returned_date = 'Null' AND (julianday('now') - julianday(Due_Date) > 0) THEN printf("%.2f",((ROUND(julianday('now') - julianday(Due_Date), 2) * LateFee)))
             ELSE '0.00' END) as LateFeeBalance
FROM ((BOOK_LOANS NATURAL JOIN BORROWER) NATURAL JOIN BOOK) NATURAL JOIN LIBRARY_BRANCH;
        """
        cursor.execute(create_view_querry)
        conn.commit()

    def search_loans_title(self):
        self.page_stack.append(self.create_main_page)
        self.clear_main_frame()

        ttk.Label(self.main_frame, text="Search by Title",
                  style="h1.TLabel").pack(pady=20)

        title_entry = ttk.Entry(
            self.main_frame, style="info.TEntry", font=('Arial', 12))

        ttk.Label(self.main_frame, text="Book Title:",
                  style="h2.TLabel").pack(pady=10)
        title_entry.pack(pady=5)

        search_button = ttk.Button(
            self.main_frame, text="Search", style="success.TButton", width=20, command=lambda: self.search_books_by_title(title_entry.get()))
        back_button = ttk.Button(self.main_frame, text="Back",
                                 style="warning.TButton", width=20, command=self.show_admin_page)

        search_button.pack(pady=10)
        back_button.pack(pady=10)

    def search_books_by_title(self, title):
        self.clear_main_frame()

        ttk.Label(self.main_frame, text=f"Search Results for '{title}'",
                  style="h1.TLabel").pack(pady=20)

        print(title)
        query_search_books = (
            "SELECT BL.Book_Id, BL.Branch_Id, COUNT(*) AS Copies "
            "FROM BOOK_LOANS BL "
            "Natural join BOOK B "
            f"WHERE B.Title LIKE '%{title}%' AND (Returned_date = 'NULL' OR Returned_date IS NULL OR " \
            f"Returned_date = 'Null') "
            "GROUP BY BL.Book_Id, BL.Branch_Id; "
        )

        cursor.execute(query_search_books)
        conn.commit()
        search_results = cursor.fetchall()

        if search_results:
            # Display search results in a treeview or any other suitable widget
            tree = ttk.Treeview(self.main_frame, columns=list(
                range(len(search_results[0]))), show="headings", height=len(search_results))

            # Add column headings
            headings = ["Book ID", "Branch ID", "Copies"]
            for i, heading in enumerate(headings):
                tree.heading(i, text=heading)
                tree.column(i, width=150)  # Adjust width as needed

            # Add data to the treeview
            for row in search_results:
                tree.insert("", "end", values=row)

            tree.pack(pady=10, padx=10)

            back_button = ttk.Button(self.main_frame, text="Back",
                                     style="warning.TButton", width=20, command=self.back_to_main_page)
            back_button.pack(pady=10)
        else:
            ttk.Label(self.main_frame, text="No results found",
                      style="h2.TLabel").pack(pady=20)
            back_button = ttk.Button(self.main_frame, text="Back",
                                     style="warning.TButton", width=20, command=self.back_to_main_page)
            back_button.pack(pady=10)

    def add_borrower(self):
        self.page_stack.append(self.create_main_page)
        self.clear_main_frame()

        ttk.Label(self.main_frame, text="Add Borrower",
                  style="h1.TLabel").pack(pady=20)

        name_entry = ttk.Entry(
            self.main_frame, style="info.TEntry", font=('Arial', 12))
        address_entry = ttk.Entry(
            self.main_frame, style="info.TEntry", font=('Arial', 12))
        phone_entry = ttk.Entry(
            self.main_frame, style="info.TEntry", font=('Arial', 12))

        ttk.Label(self.main_frame, text="Name:",
                  style="h2.TLabel").pack(pady=10)
        name_entry.pack(pady=5)

        ttk.Label(self.main_frame, text="Address:",
                  style="h2.TLabel").pack(pady=10)
        address_entry.pack(pady=5)

        ttk.Label(self.main_frame, text="Phone:",
                  style="h2.TLabel").pack(pady=10)
        phone_entry.pack(pady=5)

        add_borrower_button = ttk.Button(
            self.main_frame, text="Add Borrower", style="success.TButton", width=20, command=lambda: self.add_borrower_cmd(name_entry.get(), address_entry.get(), phone_entry.get()))
        back_button = ttk.Button(self.main_frame, text="Back",
                                 style="warning.TButton", width=20, command=self.back_to_main_page)

        add_borrower_button.pack(pady=10)
        back_button.pack(pady=10)

    # Add a new borrower without specifying card number
    def add_borrower_cmd(self, name, address, phone):
        if not name or not address or not phone:
            messagebox.showwarning(
                "Incomplete Information", "Please fill in all the fields.")
            return
        # Retrieve the card_no of the user if already exists
        query_get_card_no = f"SELECT Card_No FROM BORROWER WHERE Name = '{name}' AND Address = '{address}' AND Phone = '{phone}'"
        cursor.execute(query_get_card_no)
        card_no_result = cursor.fetchone()

        if card_no_result is not None:
            card_no = card_no_result[0]
            messagebox.showinfo("User Already Exists",
                                f"User already exists with ID: {card_no}!")
        else:
            # Insert new Borrower
            query_insert_borrower = f"INSERT INTO BORROWER (Name, Address, Phone) VALUES ('{name}', '{address}', '{phone}')"
            cursor.execute(query_insert_borrower)
            conn.commit()

            # Retrieve card_no of new user
            cursor.execute(query_get_card_no)
            card_new_result = cursor.fetchone()

            card_no = card_new_result[0]

            messagebox.showinfo(
                "Success!", f"Your card number is: {card_no} \nPlease remember this number for future logins.")

        self.back_to_main_page()

    def back_to_main_page(self):
        if self.page_stack:
            self.page_stack.pop()()

    def back_to_user_page(self):
        self.show_user_page()

    def late_days_range(self):
        self.clear_main_frame()

        start_date_label = ttk.Label(self.main_frame, text="Start Date:")
        start_date_label.pack(pady=5)
        self.start_date = tb.DateEntry(
            self.main_frame, dateformat="%Y-%m-%d", bootstyle="danger")
        self.start_date.pack(pady=5)

        end_date_label = ttk.Label(self.main_frame, text="End Date:")
        end_date_label.pack(pady=5)
        self.end_date = tb.DateEntry(
            self.main_frame, dateformat="%Y-%m-%d", bootstyle="danger")
        self.end_date.pack(pady=5)

        def set_dates():
            self.start_date_value = self.start_date.entry.get()
            self.end_date_value = self.end_date.entry.get()
            print(self.start_date_value)
            print(self.end_date_value)
        search_button = ttk.Button(self.main_frame, text="set range",
                                   style="warning.TButton", width=20, command=set_dates)
        search_button.pack(pady=10)

        search_button = ttk.Button(self.main_frame, text="Search",
                                   style="warning.TButton", width=20, command=self.search_late_books)
        search_button.pack(pady=10)

        back_button = ttk.Button(self.main_frame, text="Back",
                                 style="warning.TButton", width=20, command=self.show_admin_page)
        back_button.pack(pady=10)

        self.root.mainloop()

    def search_late_books(self):
        self.clear_main_frame()

        start_date = self.start_date_value
        end_date = self.end_date_value
        # print(start_date)
        # print(end_date)

        # Create a parameterized query to select Book_Loans that were returned late within the due date range
        query_search_late_books = (
            "SELECT B.title, CASE WHEN julianday(Returned_date) - julianday(Due_Date) > 0 THEN "
            f"julianday(Returned_date) - julianday(Due_Date) "
            f"WHEN Returned_date = 'NULL' AND julianday('now') - julianday(Due_date) > 0 "
            f"THEN ROUND(julianday('now') - julianday(Due_Date), 0) "
            f"WHEN Returned_date = 'Null' AND julianday('now') - julianday(Due_date) > 0 "
            f"THEN ROUND(julianday('now') - julianday(Due_Date), 0) "
            f"WHEN Returned_date IS NULL AND julianday('now') - julianday(Due_date) > 0 "
            f"THEN ROUND(julianday('now') - julianday(Due_Date), 0) "
            f"ELSE 0 END AS DaysLate "
            "FROM BOOK_LOANS BL natural join Book B "
            f"WHERE (Due_Date BETWEEN \"{start_date}\" AND \"{end_date}\") AND " \
            f"(Returned_date > Due_Date OR (Returned_date = 'Null' OR Returned_date = 'NULL' OR Returned_date IS NULL)) "
            "Group By B.Title "
            "ORDER BY DaysLate;"
        )
        cursor.execute(query_search_late_books)
        conn.commit()
        search_results = cursor.fetchall()

        if search_results:
            tree = ttk.Treeview(self.main_frame, columns=list(
                range(len(search_results[0]))), show="headings", height=len(search_results))

            headings = ["Book title", "Days Late"]
            for i, heading in enumerate(headings):
                tree.heading(i, text=heading)
                tree.column(i, width=250)
            # Add data to the treeview
            for row in search_results:
                tree.insert("", "end", values=row)

            tree.pack(pady=10, padx=10)

            back_button = ttk.Button(self.main_frame, text="Back",
                                     style="warning.TButton", width=20, command=self.back_to_main_page)
            back_button.pack(pady=10)
        else:
            ttk.Label(self.main_frame, text="No results found",
                      style="h2.TLabel").pack(pady=20)
            back_button = ttk.Button(self.main_frame, text="Back",
                                     style="warning.TButton", width=20, command=self.back_to_main_page)
            back_button.pack(pady=10)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = LibraryManagementSystem(tk.Tk())
    app.run()