from flask import Flask, render_template, request, redirect, url_for, flash
import openpyxl
import os
from datetime import datetime
from dotenv import load_dotenv

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend import spreadsheet_stats
from backend import log_data
from backend import generate_barcode
from backend import data_manipulation

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

EXCEL_PATH = r"C:\Users\LichKing\Desktop\Programming\Filament-Logs\filament_inventory.xlsx"

def get_sheet():
    if not os.path.exists(EXCEL_PATH):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['Timestamp', 'Barcode', 'Brand', 'Color', 'Material', 'Attribute 1', 'Attribute 2', 
                   'Filament Amount (g)', 'Location', 'Roll Weight (g)', 'Times Logged Out', 'Is Empty', 
                   'Is Favorite'])
        wb.save(EXCEL_PATH)
    wb = openpyxl.load_workbook(EXCEL_PATH)
    return wb, wb.active

@app.route("/")
def index():
    wb, sheet = get_sheet()
    filaments = [row for row in sheet.iter_rows(min_row=2, values_only=True)]
    # Sort by timestamp (first column), descending
    filaments.sort(
        key=lambda x: datetime.strptime(str(x[0]), "%Y-%m-%d %H:%M:%S") if x[0] else datetime.min,
        reverse=True
    )
    # Build favorites list
    favorite_barcodes = [f[1] for f in filaments if len(f) > 12 and str(f[12]).lower() == "true"]
    return render_template(
        "index.html",
        filaments=filaments,
        total=len(filaments),
        favorite_barcodes=favorite_barcodes
    )

@app.route("/popular")
def popular_filaments():
    wb, sheet = get_sheet()
    popular = spreadsheet_stats.get_most_popular_filaments(sheet)
    return render_template("popular.html", filaments=popular)

@app.route("/low_empty")
def low_empty_filaments():
    wb, sheet = get_sheet()
    low_empty = spreadsheet_stats.get_low_or_empty_filaments(sheet)
    return render_template("low_empty.html", filaments=low_empty)

@app.route("/empty_rolls")
def empty_rolls():
    wb, sheet = get_sheet()
    empty = spreadsheet_stats.get_empty_rolls(sheet)
    return render_template("empty_rolls.html", rolls=empty)

@app.route("/log", methods=["GET", "POST"])
def log_filament():
    if request.method == "POST":
        barcode = request.form["barcode"]
        weight = request.form["weight"]
        roll_weight = request.form.get("roll_weight", "0")
        # Use data_manipulation to decode barcode and get roll weight
        brand, color, material, attr1, attr2, location = data_manipulation.decode_barcode(barcode)
        roll_weight_val = data_manipulation.get_roll_weight(barcode, get_sheet()[1])
        filament_amount = int(weight) - int(roll_weight_val)
        result = log_data.log_filament_data_web(barcode, filament_amount, roll_weight_val)
        flash("Filament usage logged successfully!", "success")
        return redirect(url_for("index")) 
    return render_template("log.html")

@app.route("/new_roll", methods=["GET", "POST"])
def new_roll():
    wb, sheet = get_sheet()
    # Step 1: Enter filament info and generate barcode
    if request.method == "POST" and "step" not in request.form:
        brand = request.form.get("brand", "")
        color = request.form.get("color", "")
        material = request.form.get("material", "")
        attr1 = request.form.get("attribute_1", "")
        attr2 = request.form.get("attribute_2", "")
        location = request.form.get("location", "")

        # Generate barcode
        barcode = generate_barcode.generate_filament_barcode(
            brand, color, material, attr1, attr2, location, sheet
        )

        # Read weight from scale using data_manipulation
        scale_weight = None
        try:
            scale_weight, _ = data_manipulation.get_starting_weight()
        except Exception:
            scale_weight = ""

        # Show barcode and prompt for current weight (pre-fill from scale)
        return render_template(
            "new_roll.html",
            barcode=barcode,
            brand=brand,
            color=color,
            material=material,
            attribute_1=attr1,
            attribute_2=attr2,
            location=location,
            scale_weight=scale_weight,
            step="weight"
        )

    # Step 2: Enter current weight after barcode is generated
    if request.method == "POST" and request.form.get("step") == "weight":
        brand = request.form.get("brand", "")
        color = request.form.get("color", "")
        material = request.form.get("material", "")
        attr1 = request.form.get("attribute_1", "")
        attr2 = request.form.get("attribute_2", "")
        location = request.form.get("location", "")
        barcode = request.form.get("barcode", "")
        starting_weight = int(request.form.get("weight", ""))

        # Calculate roll weight for new roll
        FILAMENT_AMOUNT = data_manipulation.FILAMENT_AMOUNT  # e.g., 1000
        roll_weight = starting_weight - FILAMENT_AMOUNT
        filament_amount = starting_weight - roll_weight  # Should be FILAMENT_AMOUNT

        # Log to spreadsheet
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sheet.append([
            timestamp, barcode, brand, color, material, attr1, attr2,
            filament_amount, location, roll_weight, '0', 'False'
        ])
        wb.save(EXCEL_PATH)
        flash(f"New filament roll added! Barcode: {barcode}, Filament Amount: {filament_amount}", "success")
        return redirect(url_for("index"))

    # Initial GET: show info form
    return render_template("new_roll.html", step="info")

@app.route("/toggle_favorite", methods=["POST"])
def toggle_favorite():
    barcode = request.json.get("barcode")
    wb, sheet = get_sheet()
    for row in sheet.iter_rows(min_row=2):
        if str(row[1].value) == barcode:
            current = str(row[12].value).lower() if row[12].value else "false"
            row[12].value = "False" if current == "true" else "True"
            break
    wb.save(EXCEL_PATH)
    return '', 204

@app.route("/favorites")
def favorites():
    wb, sheet = get_sheet()
    filaments = [row for row in sheet.iter_rows(min_row=2, values_only=True)]
    unique_favorites = {}
    for f in filaments:
        if len(f) > 12 and str(f[12]).lower() == "true":
            key = (f[2], f[3], f[4], f[5], f[6])  # Brand, Color, Material, Attr1, Attr2
            if key not in unique_favorites:
                unique_favorites[key] = {
                    "brand": f[2],
                    "color": f[3],
                    "material": f[4],
                    "attribute_1": f[5],
                    "attribute_2": f[6]
                }
    return render_template("favorites.html", favorites=list(unique_favorites.values()))

if __name__ == "__main__":
    app.run(debug=True)