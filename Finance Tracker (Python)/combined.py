import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class ViewTransactionPage:
    def __init__(self, root):
        # Making the View transaction window
        self.root = root
        self.data = {}
        self.root.geometry('550x600')
        self.root.config(bg='lightgray')
        self.root.title("View Transaction")

        self.root.label = tk.Label(self.root, text="View Transactions", font=("Times New Roman", 14))
        self.root.label.grid(row=0, column=0, columnspan=4, pady=10)

        self.tree = None  # Initialize treeview widget
        self.data = []  # Data to be displayed in the treeview

        self.sort_states = {col: None for col in ("Amount", "Category", "Type", "Date")}
        self.create_transaction_table()   

    def create_transaction_table(self):
        # Create treeview widget
        self.tree = ttk.Treeview(self.root)
        self.tree["columns"] = ("Amount", "Category", "Type", "Date")
        self.tree.heading("#0", text="Transaction No.")
        self.tree.heading("Amount", text="Amount", command=lambda: self.sort_by_column("Amount"))
        self.tree.heading("Category", text="Category", command=lambda: self.sort_by_column("Category"))
        self.tree.heading("Type", text="Type", command=lambda: self.sort_by_column("Type"))
        self.tree.heading("Date", text="Date", command=lambda: self.sort_by_column("Date"))
        self.tree.column("#0", width=100)  # Transaction No.
        self.tree.column("Amount", width=100)
        self.tree.column("Category", width=100)
        self.tree.column("Type", width=100)
        self.tree.column("Date", width=100)

        # Grid treeview widget
        self.tree.grid(row=1, column=0, columnspan=4, rowspan=6, sticky="nsew")

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=4, rowspan=6, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Load transactions
        self.load_transactions()

        # Other widgets
        self.search_entry = tk.Entry(self.root, width=50)   # Create a search entry field
        self.search_entry.grid(row=8, column=0, columnspan=3, pady=5, padx=10)

        search_button = tk.Button(self.root, text="Search", command=self.search_transactions)   # Create a search button and link it to a search function
        search_button.grid(row=8, column=3, pady=10)

        self.list_view = tk.Listbox(self.root, width=70, height=10) # Create a list view to display search results
        self.list_view.grid(row=9, column=0, columnspan=4, pady=10, padx=10)

        back_button = tk.Button(self.root, text="Go Back", width=10, command=self.go_back)  # Create a back button to return to the previous screen
        back_button.grid(row=10, column=3, sticky="se", pady=(0, 10))

    def go_back(self):
        self.root.destroy()

    def load_transactions(self):
        try:
            with open("transactions.json", "r") as f:
                self.data = json.load(f)
                
        except FileNotFoundError:
            self.show_error_popup("Transactions file not found. Please create a new transaction.")
            return

        transaction_number = 1
        for category, transactions in self.data.items():
            for transaction in transactions:
                self.tree.insert("", "end", text=str(transaction_number), values=(transaction["amount"], transaction["category"], transaction["type"], transaction["date"]))
                transaction_number += 1
  
    def search_transactions(self):
        search_text = self.search_entry.get()

        # Data validation for search text
        if not search_text:
            self.show_error_message("No transacton number entered.")
            return

        # Perform search
        self.list_view.delete(0, tk.END)  # Clear the list box before adding new results
        with open("transactions.json", "r") as f:
            self.data = json.load(f)
            search_result_found = False
            for transactions in self.data.values():
                for transaction in transactions:
                    if any(search_text.lower() in str(value).lower() for value in transaction.values()):
                        self.list_view.insert(tk.END, str(transaction))
                        search_result_found = True
            if not search_result_found:
                self.show_error_message("No results found.")


    def sort_by_column(self, col):
        # Toggle sorting state for the column
        if self.sort_states[col] is None:
            self.sort_states[col] = True  # Sort in ascending order first time
        else:
            self.sort_states[col] = not self.sort_states[col]  # Toggle sorting state

        reverse = self.sort_states[col]

        if col == "Amount":
            data = [(float(self.tree.set(child, col)), child) for child in self.tree.get_children("")]
        elif col == "Date":
            data = [(datetime.strptime(self.tree.set(child, col), "%Y-%m-%d"), child) for child in self.tree.get_children("")]
        else:
            data = [(self.tree.set(child, col), child) for child in self.tree.get_children("")] 

        data.sort(reverse=reverse)
        for index, (val, child) in enumerate(data):
            self.tree.move(child, "", index)

    def show_error_message(self, message):
        messagebox.showerror("Error", message)

    def run(self):
        # Run the main event loop of the application
        self.root.mainloop()



class CLI_FinanceTracker:
    def __init__(self):
        self.transactions = {}

    def save_transactions(self):
        with open("transactions.json", "w") as file:
            json.dump(self.transactions, file, indent=4)

    def load_transactions(self):
        try:
            with open("transactions.json", "r") as file:
                self.transactions = json.load(file)
        except FileNotFoundError:
            print("Can't find any transactions. Let's get started!!")

    def add_transaction(self):
        while True:
            try:
                amount = float(input("Enter the amount: "))
                if amount < 0:
                    print("Amount cannot be negative. Try again!!")
                    continue
            except ValueError:
                print("Amount must be a number. Try again!!")
                continue
            break

        category = input("Enter the category: ").lower().capitalize()

        while True:
            type = input("Enter the type(Income/Expense): ").lower().capitalize()
            if type in ["Income", "Expense"]:
                break
            else:
                print("Type has to be either Income or Expense!!")
                continue

        while True:
            print("Please enter the date in the format YYYY-MM-DD ")
            date = input("Enter the date: ")
            try:
                datetime.strptime(date, '%Y-%m-%d').date()
                break 
            except ValueError:
                print("Invalid date format. Please try again!!")

        each_transaction = {
            "amount": amount,
            "category": category,
            "type": type,
            "date": date
        }
        
        self.categorize(each_transaction, self.transactions)
        print("\nTransaction Added Successfully!!\n")
        self.save_transactions()
        return self.transactions

    def view_transactions(self):
        count = 1
        print("")
        if len(self.transactions) == 0:
            print("No transactions available!!")
            return
        for category in self.transactions.values():
            for transaction in category:
                print("")
                print("\ntransaction_no:", count ,"\nAmount: Rs.", transaction["amount"], "\nCategory:", transaction["category"], "\nType:", transaction["type"], "\nDate:", transaction["date"])
                print("")
                count += 1

    def update_transaction(self):
        self.view_transactions()
        if len(self.transactions) == 0:
            return
        category_keys = list(self.transactions.keys())   

        try:
            while True:
                index = int(input("Enter the transaction number to update: "))
                list_index = 1

                for category in category_keys:
                    for i in range(len(self.transactions[category])):
                        if list_index == index:
                            del self.transactions[category][i]
                            self.add_transaction()
                            self.remove_category()  # Call the remove_category method here
                            self.save_transactions()
                            return
                        list_index += 1
                print("\nInvalid Transaction NUmber!!\n")
                break
        
        except ValueError:
            print("Please enter a valid transaction number!!")
        self.save_transactions()


    def delete_transaction(self):
        self.view_transactions()
        if len(self.transactions) == 0:
            return
        category_keys = list(self.transactions.keys())
        try:
            index = int(input("Enter the transaction number to delete: "))
            list_index = 1
            for category in category_keys:
                for i in range(len(self.transactions[category])):
                    if list_index == index:
                        del self.transactions[category][i]
                        self.remove_category()
                        self.save_transactions()
                        print("\nTransaction deleted successfully!!\n")
                        return
                    list_index += 1
            print("\nNo transactions available!!\n")
        except (ValueError, IndexError):
            print("Please enter a valid transaction number!!")
        self.save_transactions()

    def categorize(self, subDict, transactionDict):
        cat = subDict["category"]
        if cat in transactionDict.keys():
            transactionDict[cat].append(subDict)
        else:
            transactionDict[cat] = [subDict] 

    def summarize_transactions(self):
        if len(self.transactions) == 0:
            print("No transactions available!!")
            return
        
        income = 0
        expense = 0
        category_totals = {}

        for category, category_transactions in self.transactions.items():
            for transaction in category_transactions:
                if transaction["type"] == "Income":
                    income += transaction["amount"]
                else:
                    expense += transaction["amount"]
                    
            category_total = sum(transaction['amount'] for transaction in category_transactions)
            category_totals[category] = category_total

        print("\nTransaction Summary:")
        print(f"Total income: Rs. {income}")
        print(f"Total expense: Rs. {expense}")
        print(f"Net amount: Rs. {income - expense}")

        if category_totals:
            print("\nBy Category:")
            for category, total in category_totals.items():
                print("On", category, " : Rs.", total)

    # Function to remove each_transaction sub dictionary's category if it becomes empty
    def remove_category(self):
        keys = list(self.transactions.keys()) 
        for key in keys:
            if len(self.transactions[key]) == 0:
                del self.transactions[key]


    def main_menu(self):
        self.load_transactions()
        while True:
            print("\nPersonal Finance Tracker")
            print("\nMain Menu:")
            print("1. Add Transaction")
            print("2. View Transactions")
            print("3. Update Transaction")
            print("4. Delete Transaction")
            print("5. Display Summary")
            print("6. View Transactions through GUI")
            print("7. Exit")

            try:
                choice = int(input("Enter your choice: "))
            except ValueError:
                print("Invalid choice format. Please enter a number!!")
                continue

            if choice == 1:
                self.add_transaction()
            elif choice == 2:
                self.view_transactions()
            elif choice == 3:
                self.update_transaction()
            elif choice == 4:
                self.delete_transaction()
            elif choice == 5:
                self.summarize_transactions()
            elif choice == 6:
                self.view_transactions_GUI()
            elif choice == 7:
                print("Exiting Personal Finance Tracker...")
                break
            else:
                print("Invalid choice. Please try again!!")


    def view_transactions_GUI(self):
        print("Opening GUI for viewing transactions...")
        root = tk.Tk()
        gui = ViewTransactionPage(root)
        gui.run()


def main():
    cli = CLI_FinanceTracker()
    cli.main_menu()

if __name__ == "__main__":
    main()