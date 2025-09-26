import openpyxl
import datetime
import json

FILE_PATH = 'filament_inventory.xlsx'


workbook = openpyxl.load_workbook(FILE_PATH)
sheet = workbook.active

def get_most_popular_filaments(sheet=sheet, top_n=10):
    """ Returns the top N most popular filaments based on the times logged out. """
    popular_filaments = []

    # Loop through all rows (excluding the header)
    for row in sheet.iter_rows(min_row=2):
        brand = row[2].value
        color = row[3].value
        material = row[4].value
        attribute_1 = row[5].value if row[5].value else None
        attribute_2 = row[6].value if row[6].value else None
        times_logged_out = int(row[10].value)  # "Times Logged Out" column
        is_empty = row[11].value  # "Is Empty" column

        # If the filament is not empty, consider it in the ranking
        if is_empty:
            popular_filaments.append({
                'brand': brand,
                'color': color,
                'material': material,
                'attribute_1': attribute_1,
                'attribute_2': attribute_2,
                'times_logged_out': times_logged_out
            })

    # Sort by "Times Logged Out" in descending order
    popular_filaments.sort(key=lambda x: x['times_logged_out'], reverse=True)

    for filament in popular_filaments:
        print(f"Brand: {filament['brand']}")
        print(f"Color: {filament['color']}")
        print(f"Material: {filament['material']}")
        print(f"Attribute 1: {filament['attribute_1']}")
        print(f"Attribute 2: {filament['attribute_2']}")
        print(f"Times Logged Out: {filament['times_logged_out']}")
        print("-" * 40)

def get_low_or_empty_filaments(sheet=sheet):
    """ Returns the top N most popular filaments based on the times logged out. """
    low_or_empty_filaments = []

    # Loop through all rows (excluding the header)
    for row in sheet.iter_rows(min_row=2):
        brand = row[2].value
        color = row[3].value
        material = row[4].value
        attribute_1 = row[5].value if row[5].value else None
        attribute_2 = row[6].value if row[6].value else None
        filament_amount = row[7].value  # "Times Logged Out" column
        is_empty = row[11].value  # "Is Empty" column

        # If the filament is not empty, consider it in the ranking
        if is_empty == 'True' or float(filament_amount) < 250:
            low_or_empty_filaments.append({
                'brand': brand,
                'color': color,
                'material': material,
                'attribute_1': attribute_1,
                'attribute_2': attribute_2,
                'filament_amount': filament_amount
            })
    
    for filament in low_or_empty_filaments:
        print(f"Brand: {filament['brand']}")
        print(f"Color: {filament['color']}")
        print(f"Material: {filament['material']}")
        print(f"Attribute 1: {filament['attribute_1']}")
        print(f"Attribute 2: {filament['attribute_2']}")
        print(f"Filament Amount: {filament['filament_amount']}")
        print("-" * 40)

def get_empty_rolls(sheet=sheet):
    """ Returns the number of empty rolls in the inventory based on popularity and most recent usage. """
    empty_rolls = []

    # Loop through all rows (excluding the header)
    for row in sheet.iter_rows(min_row=2):
        last_logged = row[0].value
        brand = row[2].value
        color = row[3].value
        material = row[4].value
        attribute_1 = row[5].value if row[5].value else None
        attribute_2 = row[6].value if row[6].value else None
        times_logged_out = int(row[10].value)  # "Times Logged Out" column
        is_empty = row[11].value  # "Is Empty" column

        # If the filament is not empty, consider it in the ranking
        if is_empty:
            empty_rolls.append({
                'brand': brand,
                'color': color,
                'material': material,
                'attribute_1': attribute_1,
                'attribute_2': attribute_2,
                'times_logged_out': times_logged_out,
                'last_logged': last_logged
            })

    # Sort by "Times Logged Out" in descending order
    empty_rolls.sort(key=lambda x: datetime.datetime.strptime(x['last_logged'], "%Y-%m-%d %H:%M:%S"), reverse=True)

    for roll in empty_rolls:
        print(f"Brand: {roll['brand']}")
        print(f"Color: {roll['color']}")
        print(f"Material: {roll['material']}")
        print(f"Attribute 1: {roll['attribute_1']}")
        print(f"Attribute 2: {roll['attribute_2']}")
        print(f"Times Logged Out: {roll['times_logged_out']}")
        print(f"Last Logged: {roll['last_logged']}")
        print("-" * 40)

if __name__ == '__main__':

    # 'popular' or 'low'
    job = 'empty'

    if job == 'popular':
        get_most_popular_filaments()
    elif job == 'low':
        get_low_or_empty_filaments()
    elif job == 'empty':
        get_empty_rolls()
    else:
        print('Please use one of the correct variable strings to distinguish jobs.')