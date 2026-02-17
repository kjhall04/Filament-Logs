from datetime import datetime

from backend import generate_barcode
from backend.config import EMPTY_THRESHOLD
from backend.workbook_store import open_workbook


def _timestamp_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _to_float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _append_event(
    events_sheet,
    timestamp,
    event_type,
    barcode,
    brand,
    color,
    material,
    attr1,
    attr2,
    location,
    input_weight,
    roll_weight,
    filament_amount,
    delta_used,
    times_logged_out,
    source,
):
    if events_sheet is None:
        return

    events_sheet.append(
        [
            timestamp,
            event_type,
            barcode,
            brand,
            color,
            material,
            attr1,
            attr2,
            location,
            input_weight,
            roll_weight,
            filament_amount,
            delta_used,
            times_logged_out,
            source,
        ]
    )


def log_filament_data_web(
    barcode,
    filament_amount,
    roll_weight=None,
    total_weight=None,
    source="web",
):
    """
    Update an existing roll identified by barcode and append a usage event.
    Returns True when the barcode exists, otherwise False.
    """
    timestamp = _timestamp_now()
    target_barcode = str(barcode).strip()

    with open_workbook(write=True) as (_, inventory_sheet, events_sheet):
        for row in inventory_sheet.iter_rows(min_row=2):
            cell_barcode = row[1].value
            if cell_barcode is None or str(cell_barcode).strip() != target_barcode:
                continue

            previous_amount = _to_float(row[7].value)
            new_amount = _to_float(filament_amount, default=0.0)
            new_amount = round(max(new_amount, 0.0), 2)

            row[0].value = timestamp
            row[7].value = new_amount

            times_logged_out = _to_int(row[10].value, default=0) + 1
            row[10].value = times_logged_out

            row[11].value = "True" if new_amount <= EMPTY_THRESHOLD else "False"

            if roll_weight is not None:
                parsed_roll_weight = _to_float(roll_weight)
                if parsed_roll_weight is not None:
                    row[9].value = round(parsed_roll_weight, 2)

            delta_used = None
            if previous_amount is not None:
                delta_used = round(max(previous_amount - new_amount, 0.0), 2)

            _append_event(
                events_sheet=events_sheet,
                timestamp=timestamp,
                event_type="log_usage",
                barcode=target_barcode,
                brand=row[2].value,
                color=row[3].value,
                material=row[4].value,
                attr1=row[5].value,
                attr2=row[6].value,
                location=row[8].value,
                input_weight=round(_to_float(total_weight, default=0.0), 2)
                if total_weight is not None
                else None,
                roll_weight=round(_to_float(row[9].value, default=0.0), 2)
                if row[9].value is not None
                else None,
                filament_amount=new_amount,
                delta_used=delta_used,
                times_logged_out=times_logged_out,
                source=source,
            )
            return True

    return False


def add_new_roll_web(
    brand,
    color,
    material,
    attr1,
    attr2,
    location,
    starting_weight,
    filament_amount_target,
    barcode=None,
    source="web",
):
    """
    Add a new roll row and append an event log row.
    Returns a dict containing the inserted roll values.
    """
    timestamp = _timestamp_now()
    starting_weight_value = _to_float(starting_weight, default=0.0)
    target_amount = _to_float(filament_amount_target, default=0.0)
    roll_weight = round(starting_weight_value - target_amount, 2)

    if roll_weight < 0:
        raise ValueError("Starting weight must be at least the configured filament amount.")

    filament_amount = round(starting_weight_value - roll_weight, 2)

    with open_workbook(write=True) as (_, inventory_sheet, events_sheet):
        if not barcode:
            barcode = generate_barcode.generate_filament_barcode(
                brand,
                color,
                material,
                attr1,
                attr2,
                location,
                inventory_sheet,
            )

        barcode = str(barcode).strip()
        for row in inventory_sheet.iter_rows(min_row=2, values_only=True):
            existing = ""
            if row and len(row) > 1 and row[1] is not None:
                existing = str(row[1]).strip()
            if existing == barcode:
                raise ValueError("Barcode already exists. Please retry adding this roll.")

        is_empty = "True" if filament_amount <= EMPTY_THRESHOLD else "False"
        inventory_sheet.append(
            [
                timestamp,
                barcode,
                brand,
                color,
                material,
                attr1,
                attr2,
                filament_amount,
                location,
                roll_weight,
                0,
                is_empty,
                "False",
            ]
        )

        _append_event(
            events_sheet=events_sheet,
            timestamp=timestamp,
            event_type="new_roll",
            barcode=barcode,
            brand=brand,
            color=color,
            material=material,
            attr1=attr1,
            attr2=attr2,
            location=location,
            input_weight=round(starting_weight_value, 2),
            roll_weight=roll_weight,
            filament_amount=filament_amount,
            delta_used=0,
            times_logged_out=0,
            source=source,
        )

    return {
        "timestamp": timestamp,
        "barcode": barcode,
        "brand": brand,
        "color": color,
        "material": material,
        "attribute_1": attr1,
        "attribute_2": attr2,
        "filament_amount": filament_amount,
        "location": location,
        "roll_weight": roll_weight,
    }


def log_full_filament_data_web(brand, color, material, attr1, attr2, location, starting_weight, roll_weight):
    """
    Backwards-compatible helper retained for older code paths.
    """
    starting = _to_float(starting_weight, default=0.0)
    roll = _to_float(roll_weight, default=0.0)
    target = round(max(starting - roll, 0.0), 2)
    return add_new_roll_web(
        brand=brand,
        color=color,
        material=material,
        attr1=attr1,
        attr2=attr2,
        location=location,
        starting_weight=starting,
        filament_amount_target=target,
        source="legacy",
    )
