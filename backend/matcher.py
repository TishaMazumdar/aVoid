TRAITS = [
    "daily_rhythm",
    "lifestyle",
    "study_habits",
    "room_vibe",
    "conflict_style"
]

# Acceptable (but not perfect) matches
ACCEPTABLE_MATCHES = {
    "daily_rhythm": {
        "morning": ["night"],
        "night": ["morning"]
    },
    "lifestyle": {
        "social": ["chill"],
        "chill": ["social"]
    },
    "study_habits": {},
    "room_vibe": {
        "cozy": ["minimal"],
        "minimal": ["cozy"]
    },
    "conflict_style": {}
}

def compute_compatibility(traits1, traits2):
    """Simple matching: +2 for full match, +1 for partial (same group), 0 otherwise."""
    if not traits1 or not traits2:
        return 0

    matching_traits = 0
    total_traits = len(traits1)

    for key in traits1:
        if key in traits2:
            if traits1[key] == traits2[key]:
                matching_traits += 1

    # Normalize to a score out of 10
    score = (matching_traits / total_traits) * 10
    return score

def compute_logistics_score(user_prefs, room):
    matches = 0
    if user_prefs["room_type"] == room["type"]:
        matches += 1
    if user_prefs["floor"] == room["floor"]:
        matches += 1
    if user_prefs["has_window"] == room["has_window"]:
        matches += 1
    return (matches / 3) * 10  # Normalize to 10


def match_user_to_rooms(new_user, rooms):
    best_room = None
    best_score = -1

    for room in rooms:
        if len(room.get("occupants", [])) >= room["capacity"]:
            continue

        compatibility_total = 0

        # Roommate compatibility
        if room.get("occupants"):
            for occupant in room["occupants"]:
                compatibility_total += compute_compatibility(new_user["traits"], occupant["traits"])
            compatibility_score = compatibility_total / len(room["occupants"])
        else:
            # No roommate yet, assume neutral compatibility
            compatibility_score = 5

        # Logistics preference score
        logistics_score = compute_logistics_score(new_user["preferences"], room)

        # Debug print for individual scores
        print(f"DEBUG | Room {room['room_id']} -> Compatibility Score: {compatibility_score}, Logistics Score: {logistics_score}")

        # Weighted hybrid score
        final_score = 0.9 * compatibility_score + 0.1 * logistics_score

        if final_score > best_score:
            best_score = final_score
            best_room = room["room_id"]

    return best_room, f"{round(best_score * 10, 1)}%"