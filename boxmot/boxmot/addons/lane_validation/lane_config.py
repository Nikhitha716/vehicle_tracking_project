# boxmot/boxmot/addons/lane_validation/lane_config.py

"""
Lane abstraction configuration.

We abstract the road into vertical bands (lane regions)
for post-association validation.

This is NOT real-world lane detection.
It is a spatial consistency abstraction.
"""

# Number of lane regions (CONFIGURABLE)
NUM_LANES = 3

# Maximum allowed lane jump per frame
# 0 = same lane
# 1 = adjacent lane
# >1 = implausible
MAX_LANE_JUMP = 1

# Enable / disable lane validation
ENABLE_LANE_VALIDATION = True
