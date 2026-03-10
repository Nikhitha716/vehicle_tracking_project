# boxmot/boxmot/addons/lane_validation/lane_assigner.py

from boxmot.addons.lane_validation.lane_config import NUM_LANES


def assign_lane_id(cx, image_width):
    """
    Assign a lane ID based on the x-center of the bounding box.

    Args:
        cx (int): center x-coordinate of bounding box
        image_width (int): width of the image

    Returns:
        int: lane_id in range [0, NUM_LANES-1]
    """
    if image_width <= 0:
        return 0

    lane_width = image_width / NUM_LANES
    lane_id = int(cx / lane_width)

    # Clamp lane_id to valid range
    lane_id = max(0, min(NUM_LANES - 1, lane_id))

    return lane_id
