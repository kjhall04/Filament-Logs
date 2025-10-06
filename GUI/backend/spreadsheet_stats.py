import openpyxl
import datetime

FILE_PATH = r"C:\Users\LichKing\Desktop\Programming\Filament-Logs\filament_inventory.xlsx"

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
        times_logged_out = int(row[10].value) if row[10].value else 0
        weight = row[7].value if row[7].value else None

        popular_filaments.append({
            'brand': brand,
            'color': color,
            'material': material,
            'attribute_1': attribute_1,
            'attribute_2': attribute_2,
            'times_logged_out': times_logged_out,
            'weight': weight  # <-- Add this key
        })

    # Sort by "Times Logged Out" in descending order
    popular_filaments.sort(key=lambda x: x['times_logged_out'], reverse=True)

    return popular_filaments  # <-- Add this line

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
        is_empty = str(row[11].value).lower()  # Normalize to lowercase
        weight = row[7].value if row[7].value else None

        # If the filament is not empty, consider it in the ranking
        if is_empty == 'true' or float(filament_amount) < 250:
            low_or_empty_filaments.append({
                'brand': brand,
                'color': color,
                'material': material,
                'attribute_1': attribute_1,
                'attribute_2': attribute_2,
                'weight': weight
            })
    
    return low_or_empty_filaments

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
        is_empty = str(row[11].value).lower()  # Normalize to lowercase

        # If the filament is not empty, consider it in the ranking
        if is_empty == 'true':
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

    return empty_rolls

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