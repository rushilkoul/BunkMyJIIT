from datetime import datetime, time

def parse_time(tstr):
    """Parse time string in format 'HH:MM AM/PM' to time object"""
    return datetime.strptime(tstr, "%I:%M %p").time()


def time_overlap(start1, end1, start2, end2):
    """Check if two time intervals overlap"""
    return start1 < end2 and start2 < end1


def get_free_classes(json_data, day, check_start, check_end, campus=None):
    """
    Find all classes that are FREE during the specified day and time range.
    Returns a list of free classes with their details.
    """
    check_start = parse_time(check_start)
    check_end = parse_time(check_end)
    
    all_classes = []
    occupied_rooms = set()
    
    # Filter by campus if specified
    for batch_key, batch_data in json_data.items():
        # Skip if campus filtering is enabled and this batch doesn't match
        if campus and not batch_key.startswith(campus):
            continue
            
        day_classes = batch_data.get("classes", {}).get(day, [])
        
        for cls in day_classes:
            room = cls.get("venue", "")
            start = parse_time(cls["start"])
            end = parse_time(cls["end"])
            
            if time_overlap(start, end, check_start, check_end):
                occupied_rooms.add(room)
    
    free_classes = []
    
    for batch_key, batch_data in json_data.items():
        # Skip if campus filtering is enabled and this batch doesn't match
        if campus and not batch_key.startswith(campus):
            continue
            
        day_classes = batch_data.get("classes", {}).get(day, [])
        
        for cls in day_classes:
            room = cls.get("venue", "")
            start = parse_time(cls["start"])
            end = parse_time(cls["end"])
            
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
    
    from datetime import datetime
    current_time = datetime.now()
    current_day = current_time.strftime("%A")
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
