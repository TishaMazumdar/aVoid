# Traits being compared
TRAITS = [
    "daily_rhythm",
    "lifestyle",
    "study_habits",
    "room_vibe",
    "conflict_style"
]

# Points for scoring
PERFECT_MATCH_SCORE = 20
ACCEPTABLE_MATCH_SCORE = 10

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
    "study_habits": {
        # No acceptable cross-match defined — either compatible or not
    },
    "room_vibe": {
        "cozy": ["minimal"],
        "minimal": ["cozy"]
    },
    "conflict_style": {
        # No acceptable cross-match defined — incompatible
    }
}

def score_compatibility(p1: dict, p2: dict) -> int:
    """
    Scores compatibility between two personas based on shared traits.
    Returns a total score.
    """
    score = 0
    traits1 = p1.get("traits", {})
    traits2 = p2.get("traits", {})

    for trait in TRAITS:
        t1 = traits1.get(trait)
        t2 = traits2.get(trait)

        if not t1 or not t2:
            continue

        if t1 == t2:
            score += PERFECT_MATCH_SCORE
        elif t2 in ACCEPTABLE_MATCHES.get(trait, {}).get(t1, []):
            score += ACCEPTABLE_MATCH_SCORE

    return score

def match_user_to_rooms(new_user, rooms):
    best_room = None
    best_score = -1

    if occupants:
        for occupant in occupants:
            individual_score = score_compatibility(new_user, occupant)
            print(f"Compared with {occupant.get('name', 'Unnamed')}: {individual_score}")

    for room in rooms:
        occupants = room.get("occupants", [])
        capacity = room.get("capacity", 0)

        if len(occupants) >= capacity:
            continue  # skip full rooms

        if not occupants:
            avg_score = 0  # no one inside yet, neutral
        else:
            total_score = sum(
                score_compatibility(new_user, occupant)
                for occupant in occupants
            )
            avg_score = total_score / len(occupants)

        if avg_score > best_score:
            best_score = avg_score
            best_room = room

    if best_room:
        return best_room["room_id"], best_score
    else:
        return None, 0  # no available room