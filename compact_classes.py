import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

TIME_FMT = "%I:%M %p"

def parse_am_pm_to_minutes(time_str: str) -> int:
    dt = datetime.strptime(time_str, TIME_FMT)
    return dt.hour * 60 + dt.minute

def minutes_to_am_pm(total_minutes: int) -> str:
    base = datetime(2000, 1, 1) + timedelta(minutes=total_minutes)
    return base.strftime(TIME_FMT)

def merge_overlapping_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged: List[Tuple[int, int]] = []
    cur_start, cur_end = intervals[0]
    for s, e in intervals[1:]:
        if s < cur_end:  # overlap, not touching
            cur_end = max(cur_end, e)
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = s, e
    merged.append((cur_start, cur_end))
    return merged

def extract_campus_key(schedule_id: str) -> str:
    m = re.match(r"^\s*(btech)-(\d+)", schedule_id, flags=re.IGNORECASE)
    if m:
        return f"{m.group(1).lower()}-{m.group(2)}"
    return schedule_id.split("_", 1)[0].lower()

def build_compact(input_path: str = "classes.json", output_path: str = "classes.compact.json") -> Dict:
    with open(input_path, "r", encoding="utf-8") as f:
        raw: Dict = json.load(f)

    campus_day_room_to_intervals: Dict[str, Dict[str, Dict[str, List[Tuple[str, str]]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )

    cache_versions = []

    for schedule_id, payload in raw.items():
        campus_key = extract_campus_key(schedule_id)
        if isinstance(payload, dict) and "cacheVersion" in payload:
            cache_versions.append(payload["cacheVersion"])

        classes = payload.get("classes", {}) if isinstance(payload, dict) else {}
        for day, sessions in classes.items():
            if not isinstance(sessions, list):
                continue
            for sess in sessions:
                if not isinstance(sess, dict):
                    continue
                start = sess.get("start")
                end = sess.get("end")
                venue = sess.get("venue")
                if not start or not end or not venue:
                    continue

                venues = [v.strip() for v in str(venue).split('/') if v and str(v).strip()]
                if not venues:
                    continue
                for v in venues:
                    campus_day_room_to_intervals[campus_key][day][v].append((start, end))

    campuses_out: Dict[str, Dict] = {}
    for campus_key, day_map in campus_day_room_to_intervals.items():
        rooms_out: Dict[str, Dict[str, List[List[str]]]] = {}
        for day, room_map in day_map.items():
            for room, ses in room_map.items():
                unique = list({(s, e) for s, e in ses})
                as_minutes: List[Tuple[int, int]] = []
                for s, e in unique:
                    try:
                        as_minutes.append((parse_am_pm_to_minutes(s), parse_am_pm_to_minutes(e)))
                    except Exception:
                        continue
                as_minutes = [(s, e) for s, e in as_minutes if s < e]
                merged = merge_overlapping_intervals(as_minutes)
                serialized_pairs: List[List[str]] = [[minutes_to_am_pm(s), minutes_to_am_pm(e)] for s, e in merged]
                serialized_pairs.sort(key=lambda it: parse_am_pm_to_minutes(it[0]))

                if serialized_pairs:
                    if room not in rooms_out:
                        rooms_out[room] = {}
                    rooms_out[room][day] = serialized_pairs

        if rooms_out:
            campuses_out[campus_key] = {"rooms": rooms_out}

    meta = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z",
        "sourceCacheVersions": sorted(set(cache_versions)),
    }

    compact = {
        "meta": meta,
        "campuses": campuses_out,
    }

    pretty = json.dumps(compact, ensure_ascii=False, indent=2)

    def collapse_pairs(match):
        inside = match.group(1)
        inside = re.sub(r"\s+", " ", inside.strip())
        inside = inside.replace(" ,", ",").replace(", ", ", ")
        return f"[{inside}]"

    pretty = re.sub(
        r"\[\s*((?:\[\s*\"[^\"]+\"\s*,\s*\"[^\"]+\"\s*\]\s*,?\s*)+)\]",
        collapse_pairs,
        pretty
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty)

    return compact

if __name__ == "__main__":
    out = build_compact()
    campus_summaries = {k: len(v.get("rooms", {})) for k, v in out.get("campuses", {}).items()}
    print(json.dumps({
        "campuses": campus_summaries,
        "meta": out.get("meta", {}),
    }, indent=2))
