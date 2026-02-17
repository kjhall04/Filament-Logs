import os
from contextlib import contextmanager

import openpyxl

from backend.config import EXCEL_PATH

INVENTORY_SHEET = "Inventory"
EVENTS_SHEET = "UsageEvents"

INVENTORY_HEADERS = [
    "Timestamp",
    "Barcode",
    "Brand",
    "Color",
    "Material",
    "Attribute 1",
    "Attribute 2",
    "Filament Amount (g)",
    "Location",
    "Roll Weight (g)",
    "Times Logged Out",
    "Is Empty",
    "Is Favorite",
]

EVENT_HEADERS = [
    "Timestamp",
    "Event Type",
    "Barcode",
    "Brand",
    "Color",
    "Material",
    "Attribute 1",
    "Attribute 2",
    "Location",
    "Input Weight (g)",
    "Roll Weight (g)",
    "Filament Amount (g)",
    "Delta Used (g)",
    "Times Logged Out",
    "Source",
]

try:
    import portalocker
except Exception:
    portalocker = None


def _ensure_parent_dir():
    parent = os.path.dirname(EXCEL_PATH) or "."
    os.makedirs(parent, exist_ok=True)


def _ensure_headers(sheet, headers):
    if sheet.max_row < 1:
        sheet.append(headers)
        return

    row_one = [sheet.cell(row=1, column=idx + 1).value for idx in range(len(headers))]
    if all(value is None for value in row_one):
        for idx, header in enumerate(headers, start=1):
            sheet.cell(row=1, column=idx).value = header


def _resolve_inventory_sheet(workbook, write=False):
    if INVENTORY_SHEET in workbook.sheetnames:
        sheet = workbook[INVENTORY_SHEET]
    elif workbook.sheetnames:
        sheet = workbook[workbook.sheetnames[0]]
        if write:
            sheet.title = INVENTORY_SHEET
    else:
        if not write:
            return None
        sheet = workbook.create_sheet(INVENTORY_SHEET, 0)

    if write and sheet is not None:
        _ensure_headers(sheet, INVENTORY_HEADERS)
    return sheet


def _resolve_events_sheet(workbook, write=False):
    if EVENTS_SHEET in workbook.sheetnames:
        sheet = workbook[EVENTS_SHEET]
        if write:
            _ensure_headers(sheet, EVENT_HEADERS)
        return sheet

    if not write:
        return None

    sheet = workbook.create_sheet(EVENTS_SHEET)
    _ensure_headers(sheet, EVENT_HEADERS)
    return sheet


def _create_workbook():
    workbook = openpyxl.Workbook()
    inventory = workbook.active
    inventory.title = INVENTORY_SHEET
    inventory.append(INVENTORY_HEADERS)

    events = workbook.create_sheet(EVENTS_SHEET)
    events.append(EVENT_HEADERS)

    workbook.save(EXCEL_PATH)
    workbook.close()


@contextmanager
def _workbook_lock(write=False):
    if portalocker is None:
        yield
        return

    lock_path = EXCEL_PATH + ".lock"
    handle = open(lock_path, "a+")
    lock_flag = portalocker.LOCK_EX if write else portalocker.LOCK_SH
    portalocker.lock(handle, lock_flag)
    try:
        yield
    finally:
        try:
            portalocker.unlock(handle)
        finally:
            handle.close()


@contextmanager
def open_workbook(write=False):
    _ensure_parent_dir()
    with _workbook_lock(write=write):
        if not os.path.exists(EXCEL_PATH):
            _create_workbook()

        workbook = openpyxl.load_workbook(EXCEL_PATH)
        inventory = _resolve_inventory_sheet(workbook, write=write)
        events = _resolve_events_sheet(workbook, write=write)

        try:
            yield workbook, inventory, events
            if write:
                workbook.save(EXCEL_PATH)
        finally:
            workbook.close()


def list_inventory_rows():
    with open_workbook(write=False) as (_, inventory, _):
        if inventory is None:
            return []
        return [row for row in inventory.iter_rows(min_row=2, values_only=True)]
