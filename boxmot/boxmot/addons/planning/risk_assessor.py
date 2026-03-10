# boxmot/boxmot/addons/planning/risk_assessor.py

from boxmot.addons.planning.planning_config import (
    HIGH_RISK_THRESHOLD,
    MEDIUM_RISK_THRESHOLD,
    ADVISORIES,
)


class RiskAssessor:
    """
    Rule-based, risk-sensitive advisory planner.

    Converts behavior probabilities into:
    - Risk level (LOW / MEDIUM / HIGH)
    - Advisory message
    """

    def assess(self, probs):
        """
        Assess risk based on behavior probabilities.

        Args:
            probs (dict): behavior -> probability

        Returns:
            (risk_level, advisory)
        """
        # Risk-relevant probabilities
        lane_change_p = probs.get("LANE_CHANGE", 0.0)
        slow_down_p = probs.get("SLOW_DOWN", 0.0)

        # Aggregate risk score
        risk_score = max(lane_change_p, slow_down_p)

        if risk_score >= HIGH_RISK_THRESHOLD:
            risk = "HIGH"
        elif risk_score >= MEDIUM_RISK_THRESHOLD:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        advisory = ADVISORIES[risk]
        return risk, advisory
