# Customer Contact Manager

Customer Contact Manager is a desktop application built with Python and Tkinter that helps you manage and track customer contacts efficiently.

## Features

- Add, edit, and remove customer information
- Log customer contacts
- Set custom contact intervals for each customer
- Visual indicators for contact urgency
- Search functionality to quickly find customers
- View detailed contact history for each customer

## Requirements

- Python 3.x
- SQLite3
- Tkinter (usually comes pre-installed with Python)

## Installation

1. Clone this repository or download the source code.
2. Ensure you have Python 3.x installed on your system.
3. Place the `CCM.ico` file in the same directory as the script.

## Usage

1. Run the script using Python:

   ```
   python customer_contact_manager.py
   ```

2. The main window will appear, showing your list of customers (if any).

3. To add a new customer, click the "Add Customer" button and fill in the required information.

4. To log a contact, search for a customer, or view details, use the respective buttons next to each customer entry.

5. The color-coding system helps you quickly identify which customers need to be contacted:
   - Green: Contact not urgent
   - Yellow: Contact may be needed soon
   - Red: Contact is overdue

## Database

The application uses an SQLite database (`customers.db`) to store customer information and contact logs. This file will be created automatically in the same directory as the script when you first run the application.

## Customization

You can modify the contact urgency thresholds by adjusting the percentage values in the `refresh_list()` function.

## Troubleshooting

If you encounter any issues with the icon, ensure that the `CCM.ico` file is in the same directory as the script. If problems persist, you can comment out or remove the `root.iconbitmap(icon_path)` line in the code.

## Contributing

Contributions, bug reports, and feature requests are welcome! Feel free to submit issues or pull requests to improve the application.

## License

This project is open-source and available under the MIT License.
