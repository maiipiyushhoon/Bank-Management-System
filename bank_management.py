import sqlite3
from datetime import datetime
import os

# Clear screen function (works on Windows & Unix)
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Connect to database
def connect_db():
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (
                 acc_no INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 phone TEXT UNIQUE,
                 email TEXT,
                 pin TEXT NOT NULL DEFAULT '1234',
                 balance REAL NOT NULL DEFAULT 0.0
                 )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                 trans_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 acc_no INTEGER,
                 trans_type TEXT,
                 amount REAL,
                 details TEXT,
                 trans_date TEXT,
                 FOREIGN KEY (acc_no) REFERENCES accounts (acc_no)
                 )''')
    
    conn.commit()
    return conn

# Admin password (change if you want)
ADMIN_PASSWORD = "admin123"

# Validate PIN
def validate_pin(conn, acc_no, entered_pin):
    c = conn.cursor()
    c.execute("SELECT pin FROM accounts WHERE acc_no = ?", (acc_no,))
    result = c.fetchone()
    return result and result[0] == entered_pin

# Main menu
def main_menu(conn):
    while True:
        clear_screen()
        print("🔥" * 20)
        print("   🔥 ULTIMATE BANK MANAGEMENT SYSTEM 🔥")
        print(f"   📅 Date & Time: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        print("🔥" * 20)
        print("1. Create New Account")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Money Transfer")
        print("5. Check Balance & Details")
        print("6. View Transaction History")
        print("7. Search Account (Name/Phone)")
        print("8. Modify Account Details")
        print("9. Delete Account")
        print("10. Apply Interest (Admin)")
        print("11. List All Accounts (Admin)")
        print("12. Exit")
        print("🔥" * 20)
        
        choice = input("\nEnter your choice (1-12): ").strip()
        
        if choice == '1': create_account(conn)
        elif choice == '2': deposit(conn)
        elif choice == '3': withdraw(conn)
        elif choice == '4': transfer_money(conn)
        elif choice == '5': check_balance(conn)
        elif choice == '6': view_transactions(conn)
        elif choice == '7': search_account(conn)
        elif choice == '8': modify_account(conn)
        elif choice == '9': delete_account(conn)
        elif choice == '10': apply_interest(conn)
        elif choice == '11': list_all_accounts(conn)
        elif choice == '12':
            print("\n💥 Thank you for banking with us! Stay legendary! 💥\n")
            conn.close()
            exit()
        else:
            print("❌ Invalid choice! Try again.")
            input("Press Enter to continue...")

# Create account
def create_account(conn):
    clear_screen()
    print("--- Create New Account ---")
    name = input("Enter name: ").strip()
    phone = input("Enter phone: ").strip()
    email = input("Enter email (optional): ").strip() or "N/A"
    pin = input("Set 4-digit PIN: ").strip()
    initial = float(input("Initial deposit (min ₹500): "))
    
    if initial < 500:
        print("❌ Minimum initial deposit is ₹500!")
        input("Press Enter...")
        return
    
    if len(pin) != 4 or not pin.isdigit():
        print("❌ PIN must be 4 digits!")
        input("Press Enter...")
        return
    
    c = conn.cursor()
    try:
        c.execute("INSERT INTO accounts (name, phone, email, pin, balance) VALUES (?, ?, ?, ?, ?)",
                  (name.title(), phone, email, pin, initial))
        acc_no = c.lastrowid
        c.execute("INSERT INTO transactions (acc_no, trans_type, amount, details, trans_date) VALUES (?, 'Deposit', ?, 'Account Opened', ?)",
                  (acc_no, initial, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        print(f"\n🎉 Account created! Account No: {acc_no} | PIN: {pin}")
    except sqlite3.IntegrityError:
        print("❌ Phone number already exists!")
    
    input("\nPress Enter to continue...")

# Deposit
def deposit(conn):
    clear_screen()
    acc_no = int(input("Enter account number: "))
    pin = input("Enter PIN: ")
    if not validate_pin(conn, acc_no, pin):
        print("❌ Invalid PIN or Account!")
        input("Press Enter...")
        return
    
    amount = float(input("Enter deposit amount: "))
    if amount <= 0:
        print("❌ Amount must be positive!")
        input("Press Enter...")
        return
    
    c = conn.cursor()
    c.execute("UPDATE accounts SET balance = balance + ? WHERE acc_no = ?", (amount, acc_no))
    c.execute("INSERT INTO transactions (acc_no, trans_type, amount, details, trans_date) VALUES (?, 'Deposit', ?, 'Cash Deposit', ?)",
              (acc_no, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    c.execute("SELECT balance FROM accounts WHERE acc_no = ?", (acc_no,))
    print(f"✅ Deposited ₹{amount} | New Balance: ₹{c.fetchone()[0]}")
    input("Press Enter...")

# Withdraw
def withdraw(conn):
    clear_screen()
    acc_no = int(input("Enter account number: "))
    pin = input("Enter PIN: ")
    if not validate_pin(conn, acc_no, pin):
        print("❌ Invalid PIN or Account!")
        input("Press Enter...")
        return
    
    c = conn.cursor()
    c.execute("SELECT balance FROM accounts WHERE acc_no = ?", (acc_no,))
    balance = c.fetchone()[0]
    amount = float(input(f"Current Balance: ₹{balance}\nEnter withdraw amount: "))
    
    if amount > balance - 500:
        print("❌ Cannot withdraw! Minimum balance ₹500 must remain!")
        input("Press Enter...")
        return
    if amount <= 0:
        print("❌ Invalid amount!")
        input("Press Enter...")
        return
    
    c.execute("UPDATE accounts SET balance = balance - ? WHERE acc_no = ?", (amount, acc_no))
    c.execute("INSERT INTO transactions (acc_no, trans_type, amount, details, trans_date) VALUES (?, 'Withdraw', ?, 'Cash Withdrawal', ?)",
              (acc_no, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    print(f"✅ Withdrew ₹{amount} | Remaining: ₹{balance - amount}")
    input("Press Enter...")

# Money Transfer
def transfer_money(conn):
    clear_screen()
    sender = int(input("Your Account No: "))
    pin = input("Your PIN: ")
    if not validate_pin(conn, sender, pin):
        print("❌ Invalid credentials!")
        input("Press Enter...")
        return
    
    receiver = int(input("Receiver Account No: "))
    if sender == receiver:
        print("❌ Cannot transfer to same account!")
        input("Press Enter...")
        return
    
    c = conn.cursor()
    c.execute("SELECT balance, name FROM accounts WHERE acc_no = ?", (sender,))
    s_data = c.fetchone()
    c.execute("SELECT name FROM accounts WHERE acc_no = ?", (receiver,))
    r_data = c.fetchone()
    
    if not s_data or not r_data:
        print("❌ One or both accounts not found!")
        input("Press Enter...")
        return
    
    amount = float(input(f"Transfer to: {r_data[0]} (Acc: {receiver})\nAmount: "))
    if amount > s_data[0] - 500:
        print("❌ Insufficient balance after maintaining ₹500 min!")
        input("Press Enter...")
        return
    
    c.execute("UPDATE accounts SET balance = balance - ? WHERE acc_no = ?", (amount, sender))
    c.execute("UPDATE accounts SET balance = balance + ? WHERE acc_no = ?", (amount, receiver))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO transactions (acc_no, trans_type, amount, details, trans_date) VALUES (?, 'Transfer Out', ?, ?, ?)",
              (sender, amount, f"To Acc {receiver}", now))
    c.execute("INSERT INTO transactions (acc_no, trans_type, amount, details, trans_date) VALUES (?, 'Transfer In', ?, ?, ?)",
              (receiver, amount, f"From Acc {sender}", now))
    conn.commit()
    print(f"✅ Transfer successful! ₹{amount} sent to {r_data[0]}")
    input("Press Enter...")

# Check balance
def check_balance(conn):
    clear_screen()
    acc_no = int(input("Enter account number: "))
    pin = input("Enter PIN: ")
    if not validate_pin(conn, acc_no, pin):
        print("❌ Access denied!")
        input("Press Enter...")
        return
    
    c = conn.cursor()
    c.execute("SELECT * FROM accounts WHERE acc_no = ?", (acc_no,))
    acc = c.fetchone()
    print("\n--- Account Details ---")
    print(f"Acc No : {acc[0]}")
    print(f"Name   : {acc[1]}")
    print(f"Phone  : {acc[2]}")
    print(f"Email  : {acc[3]}")
    print(f"Balance: ₹{acc[5]}")
    input("\nPress Enter...")

# Transaction history
def view_transactions(conn):
    clear_screen()
    acc_no = int(input("Enter account number: "))
    pin = input("Enter PIN: ")
    if not validate_pin(conn, acc_no, pin):
        print("❌ Access denied!")
        input("Press Enter...")
        return
    
    c = conn.cursor()
    c.execute("SELECT trans_date, trans_type, amount, details FROM transactions WHERE acc_no = ? ORDER BY trans_date DESC", (acc_no,))
    trans = c.fetchall()
    
    if trans:
        print("\n📜 Transaction History")
        print("-" * 60)
        for t in trans:
            print(f"{t[0]} | {t[1]:12} | ₹{t[2]:8} | {t[3]}")
        print("-" * 60)
    else:
        print("No transactions yet!")
    input("\nPress Enter...")

# Search account
def search_account(conn):
    clear_screen()
    query = input("Enter name or phone to search: ").strip().lower()
    c = conn.cursor()
    c.execute("SELECT acc_no, name, phone, balance FROM accounts WHERE LOWER(name) LIKE ? OR phone LIKE ?", 
              (f"%{query}%", f"%{query}%"))
    results = c.fetchall()
    
    if results:
        print("\n🔍 Search Results")
        print("-" * 50)
        for r in results:
            print(f"Acc: {r[0]} | {r[1]:15} | {r[2]} | Balance: ₹{r[3]}")
        print("-" * 50)
    else:
        print("❌ No accounts found!")
    input("\nPress Enter...")

# Modify account
def modify_account(conn):
    clear_screen()
    acc_no = int(input("Enter account number: "))
    pin = input("Enter current PIN: ")
    if not validate_pin(conn, acc_no, pin):
        print("❌ Access denied!")
        input("Press Enter...")
        return
    
    print("\nWhat do you want to update?")
    print("1. Name\n2. Phone\n3. Email\n4. Change PIN")
    ch = input("Choice: ")
    c = conn.cursor()
    
    if ch == '1':
        new = input("New name: ")
        c.execute("UPDATE accounts SET name = ? WHERE acc_no = ?", (new.title(), acc_no))
    elif ch == '2':
        new = input("New phone: ")
        try:
            c.execute("UPDATE accounts SET phone = ? WHERE acc_no = ?", (new, acc_no))
        except sqlite3.IntegrityError:
            print("❌ Phone already in use!")
            input("Press Enter...")
            return
    elif ch == '3':
        new = input("New email: ")
        c.execute("UPDATE accounts SET email = ? WHERE acc_no = ?", (new or "N/A", acc_no))
    elif ch == '4':
        new_pin = input("New 4-digit PIN: ")
        if len(new_pin) != 4 or not new_pin.isdigit():
            print("❌ Invalid PIN!")
            input("Press Enter...")
            return
        c.execute("UPDATE accounts SET pin = ? WHERE acc_no = ?", (new_pin, acc_no))
        print("✅ PIN changed!")
    
    conn.commit()
    print("✅ Details updated!")
    input("Press Enter...")

# Delete account
def delete_account(conn):
    clear_screen()
    if input("Admin Password: ") != ADMIN_PASSWORD:
        print("❌ Access Denied!")
        input("Press Enter...")
        return
    
    acc_no = int(input("Enter account to DELETE: "))
    confirm = input(f"Type 'DELETE {acc_no}' to confirm: ")
    if confirm != f"DELETE {acc_no}":
        print("❌ Cancellation - Account safe!")
        input("Press Enter...")
        return
    
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE acc_no = ?", (acc_no,))
    c.execute("DELETE FROM accounts WHERE acc_no = ?", (acc_no,))
    conn.commit()
    print("🗑️ Account permanently deleted!")
    input("Press Enter...")

# Apply interest (Admin)
def apply_interest(conn):
    clear_screen()
    if input("Admin Password: ") != ADMIN_PASSWORD:
        print("❌ Access Denied!")
        input("Press Enter...")
        return
    
    rate = 4.0  # 4% annual
    c = conn.cursor()
    c.execute("SELECT acc_no, name, balance FROM accounts WHERE balance > 0")
    accounts = c.fetchall()
    
    print(f"Applying {rate}% interest...\n")
    for acc in accounts:
        interest = acc[2] * (rate / 100)
        new_bal = acc[2] + interest
        c.execute("UPDATE accounts SET balance = ? WHERE acc_no = ?", (new_bal, acc[0]))
        c.execute("INSERT INTO transactions (acc_no, trans_type, amount, details, trans_date) VALUES (?, 'Interest', ?, 'Annual Credit', ?)",
                  (acc[0], interest, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        print(f"{acc[1]} (Acc {acc[0]}): +₹{interest:.2f} → ₹{new_bal:.2f}")
    
    conn.commit()
    print("\n✅ Interest applied to all accounts!")
    input("Press Enter...")

# List all accounts (Admin)
def list_all_accounts(conn):
    clear_screen()
    if input("Admin Password: ") != ADMIN_PASSWORD:
        print("❌ Access Denied!")
        input("Press Enter...")
        return
    
    c = conn.cursor()
    c.execute("SELECT acc_no, name, phone, balance FROM accounts")
    accounts = c.fetchall()
    
    if accounts:
        print("\n🏦 ALL ACCOUNTS")
        print("-" * 60)
        for acc in accounts:
            print(f"Acc: {acc[0]:<6} | {acc[1]:<18} | {acc[2]:<12} | ₹{acc[3]:<10}")
        print("-" * 60)
    else:
        print("No accounts yet!")
    input("\nPress Enter...")

# START THE FIRE
if __name__ == "__main__":
    conn = connect_db()
    print("🔥 INITIALIZING ULTIMATE BANK SYSTEM 🔥")
    input("Press Enter to begin...")
    main_menu(conn)
