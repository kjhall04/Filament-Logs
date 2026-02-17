from datetime import datetime
import os

from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from backend import data_manipulation, generate_barcode, log_data, settings_store, spreadsheet_stats
from backend.config import LOW_THRESHOLD
from backend.workbook_store import open_workbook

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")


def parse_float(value, field_name):
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is required.")

    text = str(value).strip().replace(",", "")
    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid number.") from exc


def parse_timestamp(value):
    if value is None:
        return datetime.min
    if isinstance(value, datetime):
        return value

    text = str(value).strip()
    if not text:
        return datetime.min

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return datetime.min


def get_inventory_rows():
    with open_workbook(write=False) as (_, inventory_sheet, __):
        if inventory_sheet is None:
            return []
        return [row for row in inventory_sheet.iter_rows(min_row=2, values_only=True)]


def render_new_roll(step="info", **context):
    options = generate_barcode.get_catalog_options()
    app_settings = settings_store.load_settings()

    template_context = {
        "step": step,
        "brand_options": options["brands"],
        "color_options": options["colors"],
        "material_options": options["materials"],
        "attribute_options": options["attributes"],
        "location_options": options["locations"],
        "brand": "",
        "color": "",
        "material": "",
        "attribute_1": "",
        "attribute_2": "",
        "location": app_settings.get("default_location", "Lab"),
        "barcode": "",
        "scale_weight": "",
    }
    template_context.update(context)
    return render_template("new_roll.html", **template_context)


@app.context_processor
def inject_app_settings():
    return {
        "app_settings": settings_store.load_settings(),
    }


@app.route("/")
def index():
    filaments = get_inventory_rows()
    filaments.sort(key=lambda row: parse_timestamp(row[0] if row else None), reverse=True)

    favorite_barcodes = [
        row[1]
        for row in filaments
        if row and len(row) > 12 and str(row[12]).strip().lower() == "true"
    ]

    return render_template(
        "index.html",
        filaments=filaments,
        total=len(filaments),
        favorite_barcodes=favorite_barcodes,
    )


@app.route("/popular")
def popular_filaments():
    app_settings = settings_store.load_settings()
    weeks_arg = request.args.get("weeks")

    if weeks_arg is None or str(weeks_arg).strip() == "":
        default_weeks = int(app_settings.get("popular_weeks", 4))
        weeks = None if default_weeks <= 0 else default_weeks
    else:
        text = str(weeks_arg).strip().lower()
        if text == "all":
            weeks = None
        else:
            try:
                parsed = int(text)
            except ValueError:
                parsed = int(app_settings.get("popular_weeks", 4))
            weeks = None if parsed <= 0 else parsed

    popular = spreadsheet_stats.get_most_popular_filaments(top_n=100, weeks=weeks)
    selected_weeks = "all" if weeks is None else str(weeks)
    return render_template("popular.html", filaments=popular, selected_weeks=selected_weeks)


@app.route("/low_empty")
def low_empty_filaments():
    low_empty = spreadsheet_stats.get_low_or_empty_filaments()
    return render_template("low_empty.html", filaments=low_empty)


@app.route("/empty_rolls")
def empty_rolls():
    empty = spreadsheet_stats.get_empty_rolls()
    return render_template("empty_rolls.html", rolls=empty)


@app.route("/log", methods=["GET", "POST"])
def log_filament():
    form_data = {"barcode": "", "weight": ""}
    app_settings = settings_store.load_settings()

    if request.method == "POST":
        barcode = request.form.get("barcode", "").strip()
        weight_text = request.form.get("weight", "").strip()
        form_data = {"barcode": barcode, "weight": weight_text}

        if not barcode:
            flash("Barcode is required.", "error")
            return render_template("log.html", form_data=form_data)

        try:
            measured_weight = parse_float(weight_text, "Current roll weight")
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("log.html", form_data=form_data)

        with open_workbook(write=False) as (_, inventory_sheet, __):
            roll_weight_val = data_manipulation.get_roll_weight(barcode, inventory_sheet)

        if roll_weight_val is None:
            flash("Roll weight not found for this barcode.", "error")
            return render_template("log.html", form_data=form_data)

        filament_amount = round(measured_weight - float(roll_weight_val), 2)
        if filament_amount < 0:
            flash("Weight is below the recorded roll weight.", "error")
            return render_template("log.html", form_data=form_data)

        updated = log_data.log_filament_data_web(
            barcode=barcode,
            filament_amount=filament_amount,
            roll_weight=roll_weight_val,
            total_weight=measured_weight,
            source="web_log",
        )
        if not updated:
            flash("Barcode not found. Please add this roll first.", "error")
            return render_template("log.html", form_data=form_data)

        flash(f"Filament usage logged. Remaining amount: {filament_amount:.2f} g", "success")
        if app_settings.get("low_stock_alerts", True) and filament_amount < LOW_THRESHOLD:
            flash(
                f"Low-stock warning: this roll is under {LOW_THRESHOLD:.0f} g.",
                "warning",
            )
        return redirect(url_for("index"))

    return render_template("log.html", form_data=form_data)


@app.route("/api/scale_weight")
def api_scale_weight():
    weight = data_manipulation.read_scale_weight(timeout_sec=5)
    if weight is None:
        return jsonify({"error": "Scale unavailable"}), 503
    return jsonify({"weight": round(float(weight), 2)})


@app.route("/new_roll", methods=["GET", "POST"])
def new_roll():
    app_settings = settings_store.load_settings()

    if request.method == "POST" and "step" not in request.form:
        brand = request.form.get("brand", "").strip()
        color = request.form.get("color", "").strip()
        material = request.form.get("material", "").strip()
        attr1 = request.form.get("attribute_1", "").strip()
        attr2 = request.form.get("attribute_2", "").strip()
        location = request.form.get("location", app_settings.get("default_location", "Lab")).strip()

        if not brand or not color or not material:
            flash("Brand, color, and material are required.", "error")
            return render_new_roll(
                step="info",
                brand=brand,
                color=color,
                material=material,
                attribute_1=attr1,
                attribute_2=attr2,
                location=location,
            )

        try:
            with open_workbook(write=False) as (_, inventory_sheet, __):
                barcode = generate_barcode.generate_filament_barcode(
                    brand=brand,
                    color=color,
                    material=material,
                    attribute_1=attr1,
                    attribute_2=attr2,
                    location=location,
                    sheet=inventory_sheet,
                )
        except ValueError as exc:
            flash(str(exc), "error")
            return render_new_roll(
                step="info",
                brand=brand,
                color=color,
                material=material,
                attribute_1=attr1,
                attribute_2=attr2,
                location=location,
            )

        scale_weight = data_manipulation.read_scale_weight(timeout_sec=4)
        return render_new_roll(
            step="weight",
            barcode=barcode,
            brand=brand,
            color=color,
            material=material,
            attribute_1=attr1,
            attribute_2=attr2,
            location=location,
            scale_weight="" if scale_weight is None else f"{scale_weight:.2f}",
        )

    if request.method == "POST" and request.form.get("step") == "weight":
        brand = request.form.get("brand", "").strip()
        color = request.form.get("color", "").strip()
        material = request.form.get("material", "").strip()
        attr1 = request.form.get("attribute_1", "").strip()
        attr2 = request.form.get("attribute_2", "").strip()
        location = request.form.get("location", app_settings.get("default_location", "Lab")).strip()
        barcode = request.form.get("barcode", "").strip()
        weight_text = request.form.get("weight", "").strip()

        if not barcode:
            flash("Missing barcode. Please generate a barcode first.", "error")
            return render_new_roll(
                step="info",
                brand=brand,
                color=color,
                material=material,
                attribute_1=attr1,
                attribute_2=attr2,
                location=location,
            )

        try:
            starting_weight = parse_float(weight_text, "Starting weight")
        except ValueError as exc:
            flash(str(exc), "error")
            return render_new_roll(
                step="weight",
                barcode=barcode,
                brand=brand,
                color=color,
                material=material,
                attribute_1=attr1,
                attribute_2=attr2,
                location=location,
                scale_weight=weight_text,
            )

        configured_amount = float(app_settings.get("filament_amount_g", 1000.0))
        if starting_weight < configured_amount:
            flash(
                f"Starting weight must be at least {configured_amount:.2f} g based on current settings.",
                "error",
            )
            return render_new_roll(
                step="weight",
                barcode=barcode,
                brand=brand,
                color=color,
                material=material,
                attribute_1=attr1,
                attribute_2=attr2,
                location=location,
                scale_weight=weight_text,
            )

        try:
            created = log_data.add_new_roll_web(
                brand=brand,
                color=color,
                material=material,
                attr1=attr1,
                attr2=attr2,
                location=location,
                starting_weight=starting_weight,
                filament_amount_target=configured_amount,
                barcode=barcode,
                source="web_new_roll",
            )
        except ValueError as exc:
            flash(str(exc), "error")
            return render_new_roll(
                step="weight",
                barcode=barcode,
                brand=brand,
                color=color,
                material=material,
                attribute_1=attr1,
                attribute_2=attr2,
                location=location,
                scale_weight=weight_text,
            )

        flash(
            (
                f"New filament roll added. Barcode: {created['barcode']} | "
                f"Roll weight: {created['roll_weight']:.2f} g"
            ),
            "success",
        )
        return redirect(url_for("index"))

    return render_new_roll(step="info")


@app.route("/toggle_favorite", methods=["POST"])
def toggle_favorite():
    payload = request.get_json(silent=True) or {}
    barcode = str(payload.get("barcode", "")).strip()
    if not barcode:
        return jsonify({"error": "Missing barcode"}), 400

    with open_workbook(write=True) as (_, inventory_sheet, __):
        found = False
        is_favorite = False
        for row in inventory_sheet.iter_rows(min_row=2):
            cell_barcode = row[1].value
            if cell_barcode is None or str(cell_barcode).strip() != barcode:
                continue

            row_number = row[0].row
            favorite_cell = inventory_sheet.cell(row=row_number, column=13)
            current_value = str(favorite_cell.value).strip().lower() if favorite_cell.value else "false"
            is_favorite = current_value != "true"
            favorite_cell.value = "True" if is_favorite else "False"
            found = True
            break

    if not found:
        return jsonify({"error": "Barcode not found"}), 404

    return jsonify({"is_favorite": is_favorite}), 200


@app.route("/favorites")
def favorites():
    rows = get_inventory_rows()

    def key_norm(value):
        return str(value).strip().lower() if value is not None else ""

    def display_norm(value):
        return str(value).strip() if value is not None else ""

    def parse_number(value):
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            text = str(value).strip().replace(",", "")
            if not text:
                return None
            try:
                return float(text)
            except ValueError:
                return None

    counts = {}
    for row in rows:
        key = (
            key_norm(row[2] if len(row) > 2 else ""),
            key_norm(row[3] if len(row) > 3 else ""),
            key_norm(row[4] if len(row) > 4 else ""),
            key_norm(row[5] if len(row) > 5 else ""),
            key_norm(row[6] if len(row) > 6 else ""),
        )
        entry = counts.setdefault(key, {"total": 0, "low": 0})
        entry["total"] += 1

        amount = parse_number(row[7] if len(row) > 7 else None)
        if amount is not None and amount < LOW_THRESHOLD:
            entry["low"] += 1

    unique_favorites = {}
    for row in rows:
        is_favorite = len(row) > 12 and str(row[12]).strip().lower() == "true"
        if not is_favorite:
            continue

        brand = display_norm(row[2] if len(row) > 2 else "")
        color = display_norm(row[3] if len(row) > 3 else "")
        material = display_norm(row[4] if len(row) > 4 else "")
        attr1 = display_norm(row[5] if len(row) > 5 else "")
        attr2 = display_norm(row[6] if len(row) > 6 else "")

        group_key = (brand.lower(), color.lower(), material.lower(), attr1.lower(), attr2.lower())
        if group_key in unique_favorites:
            continue

        query = " ".join([brand, color, material, attr1, attr2, "filament"]).strip()
        amazon_url = "https://www.amazon.com/s?k=" + "+".join(query.split()) if query else ""

        group_counts = counts.get(group_key, {"total": 0, "low": 0})

        unique_favorites[group_key] = {
            "brand": brand,
            "color": color,
            "material": material,
            "attribute_1": attr1,
            "attribute_2": attr2,
            "amazon_url": amazon_url,
            "total_count": group_counts["total"],
            "low_count": group_counts["low"],
        }

    return render_template("favorites.html", favorites=list(unique_favorites.values()))


@app.route("/settings", methods=["GET", "POST"])
def settings():
    current = settings_store.load_settings()

    if request.method == "POST":
        updates = {
            "theme": request.form.get("theme", current.get("theme", "light")),
            "alert_mode": request.form.get("alert_mode", current.get("alert_mode", "all")),
            "rows_per_page": request.form.get("rows_per_page", current.get("rows_per_page", 20)),
            "default_location": request.form.get(
                "default_location", current.get("default_location", "Lab")
            ),
            "popular_weeks": request.form.get("popular_weeks", current.get("popular_weeks", 4)),
            "filament_amount_g": request.form.get(
                "filament_amount_g", current.get("filament_amount_g", 1000.0)
            ),
            "low_stock_alerts": request.form.get("low_stock_alerts") == "on",
        }
        settings_store.save_settings(updates)
        flash("Settings saved.", "success")
        return redirect(url_for("settings"))

    return render_template(
        "settings.html",
        settings=current,
        theme_options=settings_store.THEME_OPTIONS,
        alert_mode_options=settings_store.ALERT_MODE_OPTIONS,
    )


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug_mode)
