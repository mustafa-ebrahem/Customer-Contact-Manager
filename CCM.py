import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import os
import sys

# Custom adapter to convert datetime.date to string
def adapt_date(date):
    return date.isoformat()

# Custom converter to convert string to datetime.date
def convert_date(date_str):
    return datetime.strptime(date_str.decode(), "%Y-%m-%d").date()

# Register the adapters and converters
sqlite3.register_adapter(datetime.date, adapt_date)
sqlite3.register_converter("DATE", convert_date)

def init_db():
    conn = sqlite3.connect('customers.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, company TEXT, note TEXT, contact_interval INTEGER, last_contacted DATE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS contact_logs
                 (id INTEGER PRIMARY KEY, customer_id INTEGER, contact_date DATE, FOREIGN KEY(customer_id) REFERENCES customers(id))''')
    conn.commit()
    conn.close()

def add_customer(name, phone, company, note, contact_interval):
    conn = sqlite3.connect('customers.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    last_contacted = datetime.now().date()
    c.execute("INSERT INTO customers (name, phone, company, note, contact_interval, last_contacted) VALUES (?, ?, ?, ?, ?, ?)", 
              (name, phone, company, note, contact_interval, last_contacted))
    conn.commit()
    conn.close()
    refresh_list()

def get_customers():
    conn = sqlite3.connect('customers.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("SELECT id, name, phone, company, contact_interval, last_contacted FROM customers")
    customers = c.fetchall()
    conn.close()
    
    customers.sort(key=lambda x: (x[4] - (datetime.now().date() - x[5]).days))
    return customers


def log_contact(customer_id):
    conn = sqlite3.connect('customers.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    contact_date = datetime.now().date()
    c.execute("UPDATE customers SET last_contacted = ? WHERE id = ?", 
              (contact_date, customer_id))
    c.execute("INSERT INTO contact_logs (customer_id, contact_date) VALUES (?, ?)", 
              (customer_id, contact_date))
    conn.commit()
    conn.close()
    refresh_list()

def refresh_list():
    for widget in customer_frame.winfo_children():
        widget.destroy()
    
    customers = get_customers()
    for customer in customers:
        id, name, phone, company, contact_interval, last_contacted = customer
        days_since_last_contact = (datetime.now().date() - last_contacted).days
        days_left = contact_interval - days_since_last_contact
        percentage_left = days_left / contact_interval

        if percentage_left > 0.6:
            color = "lightgreen"
        elif percentage_left > 0.3:
            color = "yellow"
        else:
            color = "lightcoral"

        # Create customer info string including days left and contact interval
        customer_info = f"{name} {phone} {company} ({days_left}/{contact_interval})"

        frame = tk.Frame(customer_frame, bg=color, padx=5, pady=2)
        frame.pack(fill='x', padx=5, pady=2)
        tk.Label(frame, text=customer_info, bg=color, anchor='w').pack(side='left', fill='x', expand=True, padx=5)
        tk.Button(frame, text="Log", command=lambda id=id: log_contact(id)).pack(side='left', padx=5)
        tk.Button(frame, text="Details", command=lambda id=id: show_details(id)).pack(side='left', padx=5)
        tk.Button(frame, text="Edit", command=lambda id=id: edit_customer(id)).pack(side='left', padx=5)  # Add Edit button
        tk.Button(frame, text="Remove", command=lambda id=id: remove_customer(id)).pack(side='left', padx=5)

# Update the refresh_list() function to include the Edit button.



def show_details(customer_id):
    details_window = tk.Toplevel(root)
    details_window.title("Contact Details")
    details_frame = tk.Frame(details_window, padx=10, pady=10)
    details_frame.pack(fill='both', expand=True)
    
    conn = sqlite3.connect('customers.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("SELECT note FROM customers WHERE id=?", (customer_id,))
    note = c.fetchone()[0]  # Fetch the note

    tk.Label(details_frame, text="Note:", font=('Helvetica', 14, 'bold')).pack(anchor='w', pady=(0, 5))
    tk.Label(details_frame, text=note, wraplength=400).pack(anchor='w', padx=5)  # Display the note

    c.execute("SELECT contact_date FROM contact_logs WHERE customer_id = ? ORDER BY contact_date DESC", (customer_id,))
    logs = c.fetchall()
    conn.close()

    tk.Label(details_frame, text="Contact Logs:", font=('Helvetica', 14, 'bold')).pack(anchor='w', pady=(10, 5))
    for log in logs:
        tk.Label(details_frame, text=f"Contacted on: {log[0]}").pack(anchor='w', padx=5)
    
    center_window(details_window, 400, 300)

def edit_customer(customer_id):
    def save_changes():
        # Retrieve modified data from entry widgets
        new_name = name_entry.get()
        new_phone = phone_entry.get()
        new_company = company_entry.get()
        new_note = note_entry.get()
        new_contact_interval = int(contact_interval_entry.get())

        # Update customer information in the database
        conn = sqlite3.connect('customers.db', detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        c.execute("UPDATE customers SET name=?, phone=?, company=?, note=?, contact_interval=? WHERE id=?", 
                  (new_name, new_phone, new_company, new_note, new_contact_interval, customer_id))
        conn.commit()
        conn.close()

        # Refresh the customer list
        refresh_list()
        edit_window.destroy()

    # Fetch existing customer data from the database
    conn = sqlite3.connect('customers.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("SELECT name, phone, company, note, contact_interval FROM customers WHERE id=?", (customer_id,))
    customer_data = c.fetchone()
    conn.close()

    # Create a new window for editing customer data
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Customer")
    form_frame = tk.Frame(edit_window, padx=10, pady=10)
    form_frame.pack(fill='both', expand=True)

    # Populate entry widgets with existing customer data
    tk.Label(form_frame, text="Name").grid(row=0, column=0, sticky='e', padx=5, pady=5)
    name_entry = tk.Entry(form_frame)
    name_entry.grid(row=0, column=1, padx=5, pady=5)
    name_entry.insert(0, customer_data[0])  # Populate with existing name
    tk.Label(form_frame, text="Phone").grid(row=1, column=0, sticky='e', padx=5, pady=5)
    phone_entry = tk.Entry(form_frame)
    phone_entry.grid(row=1, column=1, padx=5, pady=5)
    phone_entry.insert(0, customer_data[1])  # Populate with existing phone
    tk.Label(form_frame, text="Company").grid(row=2, column=0, sticky='e', padx=5, pady=5)
    company_entry = tk.Entry(form_frame)
    company_entry.grid(row=2, column=1, padx=5, pady=5)
    company_entry.insert(0, customer_data[2])  # Populate with existing company
    tk.Label(form_frame, text="Note").grid(row=3, column=0, sticky='e', padx=5, pady=5)
    note_entry = tk.Entry(form_frame)
    note_entry.grid(row=3, column=1, padx=5, pady=5)
    note_entry.insert(0, customer_data[3])  # Populate with existing note
    tk.Label(form_frame, text="Contact Interval (days)").grid(row=4, column=0, sticky='e', padx=5, pady=5)
    contact_interval_entry = tk.Entry(form_frame)
    contact_interval_entry.grid(row=4, column=1, padx=5, pady=5)
    contact_interval_entry.insert(0, customer_data[4])  # Populate with existing contact interval
    tk.Button(form_frame, text="Save Changes", command=save_changes).grid(row=5, columnspan=2, pady=10)

    center_window(edit_window, 300, 250)



def add_customer_ui():
    def save_customer():
        name = name_entry.get()
        phone = phone_entry.get()
        company = company_entry.get()
        note = note_entry.get()
        contact_interval = int(contact_interval_entry.get())
        add_customer(name, phone, company, note, contact_interval)
        add_window.destroy()
        refresh_list()

    add_window = tk.Toplevel(root)
    add_window.title("Add Customer")
    form_frame = tk.Frame(add_window, padx=10, pady=10)
    form_frame.pack(fill='both', expand=True)

    tk.Label(form_frame, text="Name").grid(row=0, column=0, sticky='e', padx=5, pady=5)
    name_entry = tk.Entry(form_frame)
    name_entry.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(form_frame, text="Phone").grid(row=1, column=0, sticky='e', padx=5, pady=5)
    phone_entry = tk.Entry(form_frame)
    phone_entry.grid(row=1, column=1, padx=5, pady=5)
    tk.Label(form_frame, text="Company").grid(row=2, column=0, sticky='e', padx=5, pady=5)
    company_entry = tk.Entry(form_frame)
    company_entry.grid(row=2, column=1, padx=5, pady=5)
    tk.Label(form_frame, text="Note").grid(row=3, column=0, sticky='e', padx=5, pady=5)
    note_entry = tk.Entry(form_frame)
    note_entry.grid(row=3, column=1, padx=5, pady=5)
    tk.Label(form_frame, text="Contact Interval (days)").grid(row=4, column=0, sticky='e', padx=5, pady=5)
    contact_interval_entry = tk.Entry(form_frame)
    contact_interval_entry.grid(row=4, column=1, padx=5, pady=5)
    tk.Button(form_frame, text="Add", command=save_customer).grid(row=5, columnspan=2, pady=10)

    center_window(add_window, 300, 250)
    
def remove_customer(customer_id):
    conn = sqlite3.connect('customers.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    c.execute("DELETE FROM contact_logs WHERE customer_id=?", (customer_id,))
    conn.commit()
    conn.close()
    refresh_list()


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')


def search_customers(query):
    conn = sqlite3.connect('customers.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("SELECT id, name, phone, company, contact_interval, last_contacted FROM customers WHERE name LIKE ? OR phone LIKE ? OR company LIKE ?", 
              (f'%{query}%', f'%{query}%', f'%{query}%'))
    customers = c.fetchall()
    conn.close()
    
    customers.sort(key=lambda x: (x[4] - (datetime.now().date() - x[5]).days))
    return customers


def search():
    query = search_entry.get()
    if query:
        for widget in customer_frame.winfo_children():
            widget.destroy()

        customers = search_customers(query)
        if customers:
            for customer in customers:
                id, name, phone, company, contact_interval, last_contacted = customer
                days_since_last_contact = (datetime.now().date() - last_contacted).days
                days_left = contact_interval - days_since_last_contact
                percentage_left = days_left / contact_interval

                if percentage_left > 0.5:
                    color = "lightgreen"
                elif percentage_left > 0.2:
                    color = "yellow"
                else:
                    color = "lightcoral"

                customer_info = f"{name} {phone} {company} ({days_left}/{contact_interval})"

                frame = tk.Frame(customer_frame, bg=color, padx=5, pady=2)
                frame.pack(fill='x', padx=5, pady=2)
                tk.Label(frame, text=customer_info, bg=color, anchor='w').pack(side='left', fill='x', expand=True, padx=5)
                tk.Button(frame, text="Log", command=lambda id=id: log_contact(id)).pack(side='left', padx=5)
                tk.Button(frame, text="Details", command=lambda id=id: show_details(id)).pack(side='left', padx=5)
                tk.Button(frame, text="Edit", command=lambda id=id: edit_customer(id)).pack(side='left', padx=5)
                tk.Button(frame, text="Remove", command=lambda id=id: remove_customer(id)).pack(side='left', padx=5)
        else:
            messagebox.showinfo("No Results", "No customers found matching the search criteria.")

    else:
        refresh_list()  # If the search query is empty, refresh the list

def bind_enter(event):
    search()





def clear_search():
    search_entry.delete(0, 'end')
    refresh_list()



# Get the directory of the Python script
script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

# Construct the path to the icon file
icon_path = os.path.join(script_dir, "CCM.ico")





root = tk.Tk()
root.title("Customer Contact Manager")

#set the window icon
root.iconbitmap(icon_path)

# Set the size of the main window and center it
main_width = 600
main_height = 400
center_window(root, main_width, main_height)

main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack(fill='both', expand=True)

search_frame = tk.Frame(main_frame)
search_frame.pack(fill='x', padx=10, pady=(0, 10))

search_entry = tk.Entry(search_frame)
search_entry.bind('<Return>', bind_enter)
search_entry.pack(side='left', padx=5)

clear_button = tk.Button(search_frame, text="X", command=clear_search)
clear_button.pack(side='left', padx=5)

search_button = tk.Button(search_frame, text="Search", command=search)
search_button.pack(side='left', padx=5)

add_customer_button = tk.Button(search_frame, text="Add Customer", command=add_customer_ui, bg='lightblue', font=('Helvetica', 12))
add_customer_button.pack(side='right', padx=5)

customer_frame = tk.Frame(main_frame)
customer_frame.pack(fill='both', expand=True, padx=10, pady=10)

init_db()
refresh_list()

root.mainloop()
