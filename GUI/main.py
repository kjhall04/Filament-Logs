from flask import Flask, render_template, request, redirect, url_for, flash
import openpyxl
import os
from datetime import datetime

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend import data_manipulation
from backend import generate_barcode
from backend import spreadsheet_stats

app = Flask(__name__)
app.secret_key = "filament_secret"

EXCEL_PATH = os.path.join(os.path.dirname(__file__), "..", "filament_inventory.xlsx")

def get_sheet():
    if not os.path.exists(EXCEL_PATH):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['Timestamp', 'Barcode', 'Brand', 'Color', 'Material', 'Attribute 1', 'Attribute 2', 
                   'Filament Amount (g)', 'Location', 'Roll Weight (g)', 'Times Logged Out', 'Is Empty'])
        wb.save(EXCEL_PATH)
    wb = openpyxl.load_workbook(EXCEL_PATH)
    return wb, wb.active

@app.route("/")
def index():
    wb, sheet = get_sheet()
    filaments = [row for row in sheet.iter_rows(min_row=2, values_only=True)]
    filaments.reverse()  # Show most recent first
    # Pagination
    page = int(request.args.get("page", 1))
    per_page = 20
    total = len(filaments)
    pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    filaments_page = filaments[start:end]
    return render_template(
        "index.html",
        filaments=filaments_page,
        page=page,
        pages=pages,
        total=total
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
        brand = request.form.get("brand", "")
        color = request.form.get("color", "")
        material = request.form.get("material", "")
        attribute_1 = request.form.get("attribute_1", "")
        attribute_2 = request.form.get("attribute_2", "")
        location = request.form.get("location", "")
        roll_weight = request.form.get("roll_weight", "")
        times_logged_out = request.form.get("times_logged_out", "1")

        # Validate barcode using your function (pass barcode to function)
        if not data_manipulation.decode_barcode(barcode):
            flash("Invalid barcode!", "danger")
            return redirect(url_for("log_filament"))

        # Optionally, get current weight from scale if needed
        # current_weight = data_manipulation.get_current_weight(roll_weight)

        wb, sheet = get_sheet()
        sheet.append([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            barcode,
            brand,
            color,
            material,
            attribute_1,
            attribute_2,
            weight,
            location,
            roll_weight,
            times_logged_out,
            "False"
        ])
        wb.save(EXCEL_PATH)
        flash("Filament usage logged successfully!", "success")
        return redirect(url_for("index"))
    return render_template("log.html")

@app.route("/new_roll", methods=["GET", "POST"])
def new_roll():
    if request.method == "POST":
        wb, sheet = get_sheet()
        # Prompt for info (simulate by getting from form)
        brand = request.form.get("brand", "")
        color = request.form.get("color", "")
        material = request.form.get("material", "")
        attribute_1 = request.form.get("attribute_1", "")
        attribute_2 = request.form.get("attribute_2", "")
        location = request.form.get("location", "")

        # Generate barcode using your function
        barcode = generate_barcode.generate_filament_barcode(
            brand, color, material, attribute_1, attribute_2, location, sheet
        )

        # Get starting weight from scale (simulate or use actual function)
        starting_weight = data_manipulation.get_starting_weight()

        sheet.append([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            barcode,
            brand,
            color,
            material,
            attribute_1,
            attribute_2,
            starting_weight,
            location,
            starting_weight,
            "0",
            "False"
        ])
        wb.save(EXCEL_PATH)
        flash(f"New filament roll added! Barcode: {barcode}, Starting Weight: {starting_weight}", "success")
        return redirect(url_for("index"))
    return render_template("new_roll.html")

if __name__ == "__main__":
    app.run(debug=True)