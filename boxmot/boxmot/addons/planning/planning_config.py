# boxmot/boxmot/addons/planning/planning_config.py

"""
Configuration for risk-sensitive advisory planning.
"""

# Enable / disable planning module
ENABLE_PLANNING = True

# Risk thresholds (based on probabilities)
# These are heuristic and explainable
HIGH_RISK_THRESHOLD = 0.6
MEDIUM_RISK_THRESHOLD = 0.3

# Advisory messages
ADVISORIES = {
    "LOW": "Maintain speed",
    "MEDIUM": "Prepare to slow down",
    "HIGH": "Slow down / increase gap",
}
