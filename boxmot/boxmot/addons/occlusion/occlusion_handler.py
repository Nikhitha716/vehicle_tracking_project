# boxmot/boxmot/addons/occlusion/occlusion_handler.py

from .occlusion_config import MIN_OCCLUSION_FRAMES, MAX_OCCLUSION_FRAMES


class OcclusionHandler:
    """
    Handles occlusion lifecycle:
    - decides when a track becomes occluded
    - removes occlusion when track reappears
    """

    def __init__(self):
        # track_id -> consecutive missing frames
        self.missing_counter = {}

    def update_visible(self, track_id):
        """
        Called when a track is visible in the current frame.
        Resets missing counter and clears occlusion state.
        """
        if track_id in self.missing_counter:
            del self.missing_counter[track_id]

    def update_missing(self, track_id):
        """
        Called when a track is missing in the current frame.
        """
        self.missing_counter[track_id] = self.missing_counter.get(track_id, 0) + 1

    def is_occluded(self, track_id):
        """
        Returns True if track is considered occluded.
        """
        missed = self.missing_counter.get(track_id, 0)
        return MIN_OCCLUSION_FRAMES <= missed <= MAX_OCCLUSION_FRAMES

    def cleanup(self):
        """
        Remove stale tracks that exceeded max occlusion duration.
        """
        for tid in list(self.missing_counter.keys()):
            if self.missing_counter[tid] > MAX_OCCLUSION_FRAMES:
                del self.missing_counter[tid]
