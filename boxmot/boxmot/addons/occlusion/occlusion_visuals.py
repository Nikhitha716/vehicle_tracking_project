# boxmot/boxmot/addons/occlusion/occlusion_visuals.py

import cv2
from boxmot.addons.occlusion.occlusion_config import (
    OCCLUDED_TEXT_COLOR,
    TRAJECTORY_COLOR,
    MAX_TRAJECTORY_LENGTH,
)

def draw_trajectory(img, points):
    pts = list(points)[-MAX_TRAJECTORY_LENGTH:]
    for i in range(1, len(pts)):
        cv2.line(img, pts[i - 1], pts[i], TRAJECTORY_COLOR, 2)

def draw_occlusion_text(img, track_id, position):
    x, y = position
    cv2.putText(
        img,
        f"ID {track_id} (occluded)",
        (x - 30, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        OCCLUDED_TEXT_COLOR,
        2
    )

def draw_occlusion_panel(img, occluded_ids, reappeared_ids, anchor="left"):
    """
    Draws a clean occlusion status panel.
    """
    x = 20 if anchor == "left" else img.shape[1] - 260
    y = 40
    line_h = 22

    cv2.putText(
        img,
        "Occlusion Status",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )

    y += line_h

    for tid in sorted(occluded_ids):
        cv2.putText(
            img,
            f"ID {tid} : OCCLUDED",
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 165, 255),  # orange
            2,
        )
        y += line_h

    for tid in reappeared_ids:
        cv2.putText(
            img,
            f"ID {tid} : RE-IDENTIFIED",
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),  # white
            2,
        )
        y += line_h

