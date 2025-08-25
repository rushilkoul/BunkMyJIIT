import os
import sys
import json
from openpyxl import load_workbook

EXCEL_FILE = "RoomLocation.xlsx"
JSON_FILE = "room_lookup.json"

room_lookup = {}


def generate_json_from_excel():
    wb = load_workbook(EXCEL_FILE, data_only=True)
    ws = wb.active

    headers = {cell.value: idx for idx, cell in enumerate(ws[1], start=1)}

    lookup = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        room_id = str(row[headers["ROOMID"] - 1])
        building = row[headers["BUILDING"] - 1]
        floor = row[headers["FLOOR"] - 1]
        lookup[room_id] = f"{building} ({floor})"

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(lookup, f, ensure_ascii=False, indent=2)

    print(f"Generated {JSON_FILE} from {EXCEL_FILE}")
    return lookup


def load_room_lookup():
    global room_lookup
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            room_lookup = json.load(f)
    else:
        print(f"{JSON_FILE} not found. Run with -generate to create it.")
        room_lookup = {}


def getLocation(roomID):
    return room_lookup.get(str(roomID), None)

# CLI mode
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-generate":
        room_lookup = generate_json_from_excel()
    else:
        load_room_lookup()
        print("Room lookup loaded. Try: getLocation('101')")
