# boxmot/boxmot/addons/occlusion/occlusion_config.py

# Occlusion detection stability
MIN_OCCLUSION_FRAMES = 8
MAX_OCCLUSION_FRAMES = 30

# Visualization limits
MAX_OCCLUSIONS_TO_DRAW = 3   # HARD CAP
MAX_TRAJECTORY_LENGTH = 15   # frames

# Colors (BGR)
OCCLUDED_TEXT_COLOR = (0, 165, 255)   # orange
TRAJECTORY_COLOR = (255, 255, 255)    # white
