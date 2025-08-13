import json
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, time
from flask_cors import CORS


def parse_time(tstr):
    """Parse time string in format 'HH:MM AM/PM' to time object"""
    return datetime.strptime(tstr, "%I:%M %p").time()


def time_overlap(start1, end1, start2, end2):
    """Check if two time intervals overlap"""
    return start1 < end2 and start2 < end1


def get_free_classes(json_data, day, check_start, check_end):
    """
    Find all classes that are FREE during the specified day and time range.
    Returns a list of free classes with their details.
    """
    check_start = parse_time(check_start)
    check_end = parse_time(check_end)
    
    # Get all classes for the specified day
    all_classes = []
    occupied_rooms = set()
    
    for batch_key, batch_data in json_data.items():
        day_classes = batch_data.get("classes", {}).get(day, [])
        
        for cls in day_classes:
            room = cls.get("venue", "")
            start = parse_time(cls["start"])
            end = parse_time(cls["end"])
            
            # Check if this class overlaps with our time range
            if time_overlap(start, end, check_start, check_end):
                occupied_rooms.add(room)
    
    # Now find all classes that are NOT occupied during this time
    free_classes = []
    
    for batch_key, batch_data in json_data.items():
        day_classes = batch_data.get("classes", {}).get(day, [])
        
        for cls in day_classes:
            room = cls.get("venue", "")
            start = parse_time(cls["start"])
            end = parse_time(cls["end"])
            
            # If room is not occupied during our time range, it's free
            if room not in occupied_rooms:
                free_classes.append({
                    "room": room,
                    "batch": batch_key,
                    "subject": cls.get("subject", ""),
                    "subject_code": cls.get("subjectcode", ""),
                    "teacher": cls.get("teacher", ""),
                    "type": cls.get("type", ""),
                    "start": cls["start"],
                    "end": cls["end"]
                })
    
    # Remove duplicates based on room (since multiple batches might have the same room free)
    unique_free_classes = []
    seen_rooms = set()
    
    for cls in free_classes:
        if cls["room"] not in seen_rooms:
            unique_free_classes.append(cls)
            seen_rooms.add(cls["room"])
    
    return sorted(unique_free_classes, key=lambda x: x["room"])


def search_teacher(json_data, teacher_name):
    """
    Search for a teacher by name and return their current class schedule.
    Returns the teacher's current room and class details.
    """
    teacher_name = teacher_name.strip().lower()
    teacher_classes = []
    
    # Get current day and time
    from datetime import datetime
    current_time = datetime.now()
    current_day = current_time.strftime("%A")  # Monday, Tuesday, etc.
    current_time_obj = current_time.time()
    
    for batch_key, batch_data in json_data.items():
        day_classes = batch_data.get("classes", {}).get(current_day, [])
        
        for cls in day_classes:
            if teacher_name in cls.get("teacher", "").lower():
                start = parse_time(cls["start"])
                end = parse_time(cls["end"])
                
                # Check if this class is currently happening
                is_current = start <= current_time_obj <= end
                
                teacher_classes.append({
                    "batch": batch_key,
                    "subject": cls.get("subject", ""),
                    "subject_code": cls.get("subjectcode", ""),
                    "teacher": cls.get("teacher", ""),
                    "room": cls.get("venue", ""),
                    "type": cls.get("type", ""),
                    "start": cls["start"],
                    "end": cls["end"],
                    "day": current_day,
                    "is_current": is_current
                })
    
    return teacher_classes


# Load the classes data
classes_data = None
try:
    with open("classes.json", encoding="utf-8") as f:
        classes_data = json.load(f)
    print("Successfully loaded classes.json")
except Exception as e:
    print(f"Error loading classes.json: {e}")
    classes_data = None

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return send_from_directory("./frontend/", "index.html")

@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory("./frontend", filename)


@app.route("/tabledata", methods=["POST"])
def get_free_classes_endpoint():
    """Endpoint to get free classes for a specific day and time range"""
    print("Received a request for free classes")
    
    if not classes_data:
        return jsonify({
            "status": "error",
            "message": "Classes data not loaded"
        }), 500
    
    try:
        data = request.get_json()
        day = data.get('day')
        from_time = data.get('from')
        to_time = data.get('to')
        
        if not all([day, from_time, to_time]):
            return jsonify({
                "status": "error",
                "message": "Missing required parameters: day, from, to"
            }), 400
        
        free_classes = get_free_classes(classes_data, day, from_time, to_time)
        
        response_data = {
            "status": "success",
            "free_classes": free_classes,
            "count": len(free_classes)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/teacher", methods=["POST"])
def search_teacher_endpoint():
    """Endpoint to search for a teacher and get their current class"""
    print("Received a request to search for teacher")
    
    if not classes_data:
        return jsonify({
            "status": "error",
            "message": "Classes data not loaded"
        }), 500
    
    try:
        data = request.get_json()
        teacher_name = data.get('teacher_name')
        
        if not teacher_name:
            return jsonify({
                "status": "error",
                "message": "Missing required parameter: teacher_name"
            }), 400
        
        teacher_classes = search_teacher(classes_data, teacher_name)
        
        if not teacher_classes:
            response_data = {
                "status": "success",
                "message": f"No classes found for teacher: {teacher_name}",
                "teacher_classes": []
            }
        else:
            response_data = {
                "status": "success",
                "teacher_classes": teacher_classes,
                "count": len(teacher_classes)
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)