import os
import json
from openpyxl import load_workbook

EXCEL_FILE = "RoomLocation.xlsx"
JSON_FILE = "room_lookup.json"

room_lookup = {}

def load_room_lookup():
    global room_lookup
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            room_lookup = json.load(f)
    else:

        wb = load_workbook(EXCEL_FILE, data_only=True)
        ws = wb.active

        headers = {cell.value: idx for idx, cell in enumerate(ws[1], start=1)}

        room_lookup = {}
        for row in ws.iter_rows(min_row=2, values_only=True):
            room_id = str(row[headers["ROOMID"] - 1])
            building = row[headers["BUILDING"] - 1]
            floor = row[headers["FLOOR"] - 1]
            room_lookup[room_id] = f"{building} ({floor})"

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(room_lookup, f, ensure_ascii=False, indent=2)

def getLocation(roomID):
    if not room_lookup:
        load_room_lookup()
    return room_lookup.get(str(roomID), None)
