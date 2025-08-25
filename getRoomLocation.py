import pandas as pd

df = pd.read_excel('RoomLocation.xlsx', usecols=['ROOMID', 'BUILDING', 'FLOOR'])

room_lookup = {
    str(row['ROOMID']): f"{row['BUILDING']}_{row['FLOOR']}"
    for _, row in df.iterrows()
}

def getLocation(roomID):
    return room_lookup.get(str(roomID), None)