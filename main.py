from flask import Flask, request, jsonify, send_from_directory
import json
import util
from flask_cors import CORS
from getRoomLocation import getLocation


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

@app.route("/checkteacher")
def checkTeacher():
    return send_from_directory("./frontend/", "checkTeacher.html")

@app.route("/checkroom")
def checkRoom():
    return send_from_directory("./frontend/", "checkRoom.html")

@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory("./frontend", filename)


@app.route("/api/tabledata", methods=["POST"])
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
        campus = data.get('campus')  # Get campus parameter
        
        print(f"Request data: day={day}, from={from_time}, to={to_time}, campus={campus}")
        
        if not all([day, from_time, to_time]):
            return jsonify({
                "status": "error",
                "message": "Missing required parameters: day, from, to"
            }), 400
        free_classes = util.get_free_classes(classes_data, day, from_time, to_time, campus)
        
        print(f"Found {len(free_classes)} free classes for campus {campus}")
        
        response_data = {
            "status": "success",
            "free_classes": free_classes,
            "count": len(free_classes)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in get_free_classes_endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/getRoomLocations", methods=["POST"])
def getRoomLocs():
    """Endpoint to search multiple room names and find locations"""
    try:
        data = request.get_json()
        room_ids = data.get("room_ids", [])

        if not isinstance(room_ids, list):
            return jsonify({
                "status": "error",
                "message": "room_ids must be a list"
            }), 400

        results = {str(rid): getLocation(rid) for rid in room_ids}

        return jsonify({
            "status": "success",
            "locations": results
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

        
@app.route("/api/teacher", methods=["POST"])
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
        
        teacher_classes = util.search_teacher(classes_data, teacher_name)
        
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

@app.route("/api/getallrooms", methods=["GET"])
def get_all_rooms_endpoint():
    """Endpoint to get all rooms for a campus"""
    print("Received a request to get all rooms")
    
    if not classes_data:
        return jsonify({
            "status": "error",
            "message": "Classes data not loaded"
        }), 500
    
    try:
        campus = request.args.get('campus')
        
        rooms = util.get_all_rooms(classes_data, campus)
        
        return jsonify({
            "status": "success",
            "rooms": rooms,
            "count": len(rooms)
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/checkrooms", methods=["POST"])
def check_rooms_endpoint():
    """Endpoint to check if specific rooms are available"""
    print("Received a request to check rooms")
    
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
        campus = data.get('campus')
        rooms = data.get('rooms', [])
        
        if not all([day, from_time, to_time, rooms]):
            return jsonify({
                "status": "error",
                "message": "Missing required parameters"
            }), 400
        
        availability = util.check_room_availability(classes_data, day, from_time, to_time, campus, rooms)
        
        return jsonify({
            "status": "success",
            "availability": availability
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# apparently Vercel never runs the main block 
# so its actually fine to leave this in
# i can test locally again wooooo
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
