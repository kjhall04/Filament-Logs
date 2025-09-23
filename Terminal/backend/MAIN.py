import sys

import log_data
import spreadsheet_stats

def print_menu(is_admin):
    print("\nFilament Logs Terminal Menu")
    print("1. Log filament usage (update weight)")
    if is_admin:
        print("2. Log new filament roll (add new barcode)")
        print("3. Show most popular filaments")
        print("4. Show low or empty filaments")
        print("5. Show empty rolls (sorted by most recent usage)")
    print("0. Exit")

def main(user):
    is_admin = (user == 'Admin')

    while True:
        print_menu(is_admin)
        choice = input("Select an option: ").strip()
        if choice == '1':
            log_data.log_filament_data()
        elif choice == '2' and is_admin:
            log_data.log_full_filament_data()
        elif choice == '3' and is_admin:
            spreadsheet_stats.get_most_popular_filaments()
        elif choice == '4' and is_admin:
            spreadsheet_stats.get_low_or_empty_filaments()
        elif choice == '5' and is_admin:
            spreadsheet_stats.get_empty_rolls()
        elif choice == '0':
            print("Exiting Filament Logs Terminal. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Change this to 'Admin' or 'None' to test different roles
    user = None

    main(user)