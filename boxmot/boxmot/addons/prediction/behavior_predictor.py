# boxmot/boxmot/addons/prediction/behavior_predictor.py

from boxmot.addons.prediction.prediction_config import (
    BEHAVIORS,
    LANE_CHANGE_THRESHOLD,
    SPEED_DROP_THRESHOLD,
)


class BehaviorPredictor:
    """
    Heuristic, uncertainty-aware behavior predictor.

    Produces a probability distribution over:
    KEEP_LANE, LANE_CHANGE, SLOW_DOWN
    """

    def __init__(self):
        # track_id -> previous speed
        self.prev_speed = {}

    def predict(self, track_id, curr_lane, prev_lane, speed):
        """
        Predict behavior probabilities.

        Args:
            track_id (int)
            curr_lane (int)
            prev_lane (int or None)
            speed (float): pixels/frame

        Returns:
            dict: behavior -> probability
        """

        # Default scores
        scores = {
            "KEEP_LANE": 1.0,
            "LANE_CHANGE": 0.5,
            "SLOW_DOWN": 0.5,
        }

        # Lane-based heuristic
        if prev_lane is not None:
            if abs(curr_lane - prev_lane) >= LANE_CHANGE_THRESHOLD:
                scores["LANE_CHANGE"] += 1.5
                scores["KEEP_LANE"] -= 0.5

        # Speed-based heuristic
        prev_speed = self.prev_speed.get(track_id, speed)
        if prev_speed - speed > SPEED_DROP_THRESHOLD:
            scores["SLOW_DOWN"] += 1.5
            scores["KEEP_LANE"] -= 0.5

        # Store speed
        self.prev_speed[track_id] = speed

        # Normalize to probabilities
        total = sum(max(v, 0.01) for v in scores.values())
        probs = {
            k: max(v, 0.01) / total
            for k, v in scores.items()
        }

        return probs
