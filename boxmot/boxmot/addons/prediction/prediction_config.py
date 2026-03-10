# boxmot/boxmot/addons/prediction/prediction_config.py

"""
Configuration for uncertainty-aware heuristic prediction.
"""

# Prediction interval (in frames)
PREDICTION_INTERVAL = 5

# Behavior labels
BEHAVIORS = ["KEEP_LANE", "LANE_CHANGE", "SLOW_DOWN"]

# Heuristic thresholds
LANE_CHANGE_THRESHOLD = 1        # lane difference
SPEED_DROP_THRESHOLD = 2.0       # pixels/frame (heuristic)

# Enable prediction module
ENABLE_PREDICTION = True
