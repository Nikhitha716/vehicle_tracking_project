# boxmot/boxmot/addons/lane_validation/lane_state.py

class LaneState:
    """
    Maintains lane history for each tracked vehicle.

    This class does NOT perform validation.
    It only stores state.
    """

    def __init__(self):
        # track_id -> current lane_id
        self.current_lane = {}

        # track_id -> previous lane_id
        self.previous_lane = {}

        # track_id -> last frame index seen
        self.last_seen_frame = {}

    def update(self, track_id, lane_id, frame_idx):
        """
        Update lane state for a track.

        Args:
            track_id (int)
            lane_id (int)
            frame_idx (int)
        """
        if track_id in self.current_lane:
            self.previous_lane[track_id] = self.current_lane[track_id]

        self.current_lane[track_id] = lane_id
        self.last_seen_frame[track_id] = frame_idx

    def get_current_lane(self, track_id):
        return self.current_lane.get(track_id, None)

    def get_previous_lane(self, track_id):
        return self.previous_lane.get(track_id, None)

    def is_new_track(self, track_id):
        return track_id not in self.previous_lane

    def remove_track(self, track_id):
        """
        Optional cleanup if needed later.
        """
        self.current_lane.pop(track_id, None)
        self.previous_lane.pop(track_id, None)
        self.last_seen_frame.pop(track_id, None)
        
