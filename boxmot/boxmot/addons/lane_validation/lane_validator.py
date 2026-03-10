# boxmot/boxmot/addons/lane_validation/lane_validator.py

from boxmot.addons.lane_validation.lane_config import MAX_LANE_JUMP


def validate_lane_transition(track_id, prev_lane, curr_lane):
    """
    Validate lane continuity for a track.

    Returns:
        event_type (str): VALID | LANE_JUMP
    """
    if prev_lane is None:
        return "VALID"

    if abs(curr_lane - prev_lane) <= MAX_LANE_JUMP:
        return "VALID"

    return "LANE_JUMP"
