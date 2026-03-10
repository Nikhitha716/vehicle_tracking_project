# boxmot/boxmot/addons/overtaking/focus_selector.py

class FocusVehicleSelector:
    """
    Selects a focus vehicle for visualization only.
    """

    def __init__(self, lock_frames=100):
        self.focus_id = None
        self.lock_frames = lock_frames
        self.lock_counter = 0

    def select(self, tracks, image_width, manual_focus_id=None):
        """
        Select focus vehicle.

        Args:
            tracks: list of tracked detections
            image_width: width of video frame
            manual_focus_id: user-specified focus ID (optional)

        Returns:
            focus_id (int or None)
        """

        # Manual override always wins
        if manual_focus_id is not None:
            self.focus_id = manual_focus_id
            self.lock_counter = self.lock_frames
            return self.focus_id

        # Keep current focus if locked
        if self.focus_id is not None and self.lock_counter > 0:
            self.lock_counter -= 1
            return self.focus_id

        # Auto-select: closest to image center
        center_x = image_width // 2
        min_dist = float("inf")
        chosen_id = None

        for t in tracks:
            x1, _, x2, _, tid = map(int, t[:5])
            cx = (x1 + x2) // 2
            dist = abs(cx - center_x)

            if dist < min_dist:
                min_dist = dist
                chosen_id = tid

        self.focus_id = chosen_id
        self.lock_counter = self.lock_frames
        return self.focus_id
