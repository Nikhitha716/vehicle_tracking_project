# boxmot/boxmot/addons/occlusion/occlusion_state.py

from collections import defaultdict, deque

class OcclusionState:
    def __init__(self, missing_threshold=15, trajectory_len=15):
        self.missing_threshold = missing_threshold

        # track_id -> consecutive missed frames
        self.missed_counts = defaultdict(int)

        # track_id -> last visible center (cx, cy)
        self.last_positions = {}

        # track_id -> trajectory deque
        self.trajectories = defaultdict(lambda: deque(maxlen=trajectory_len))

    def update_visible(self, track_id, center):
        """Call when track is visible in current frame"""
        self.missed_counts[track_id] = 0
        self.last_positions[track_id] = center
        self.trajectories[track_id].append(center)

    def mark_missed(self, track_id):
        """Call when track not visible in current frame"""
        self.missed_counts[track_id] += 1

    def is_occluded(self, track_id):
        """Return True if track is considered occluded"""
        return self.missed_counts.get(track_id, 0) >= self.missing_threshold



