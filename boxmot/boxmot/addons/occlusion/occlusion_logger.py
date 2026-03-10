# boxmot/boxmot/addons/occlusion/occlusion_logger.py

class OcclusionLogger:
    def __init__(self):
        self.prev_state = {}  # track_id -> occluded(True/False)

    def log_state(self, track_id, is_occluded, frame_index):
        """
        Logs state transitions:
        - visible -> occluded
        - occluded -> recovered
        """
        previous = self.prev_state.get(track_id, False)

        # Transition: visible -> occluded
        if not previous and is_occluded:
            print(f"[OCCLUSION] ID {track_id} occluded at frame {frame_index}")

        # Transition: occluded -> visible (recovered)
        if previous and not is_occluded:
            print(f"[RECOVERY] ID {track_id} recovered at frame {frame_index}")

        self.prev_state[track_id] = is_occluded
