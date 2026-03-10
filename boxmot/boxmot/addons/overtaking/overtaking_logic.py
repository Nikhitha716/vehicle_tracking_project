# boxmot/boxmot/addons/overtaking/overtaking_logic.py

class OvertakingAdvisor:
    """
    Advisory-only overtaking feasibility assessment.
    """

    def assess(
        self,
        lane_id,
        lead_vehicle_present,
        relative_speed,
        adjacent_lane_available,
        occlusion_ahead,
        risk_level,
        uncertainty_high,
    ):
        """
        Decide overtaking feasibility.

        Returns:
            (state, reason)
            state ∈ {"SAFE", "RISKY", "NOT ADVISED"}
        """

        # No vehicle ahead → no overtaking scenario
        if not lead_vehicle_present:
            return "NOT ADVISED", "no lead vehicle"

        # No adjacent lane → cannot overtake
        if not adjacent_lane_available:
            return "NOT ADVISED", "no adjacent lane available"

        # Occlusion ahead → unsafe
        if occlusion_ahead:
            return "RISKY", "occlusion ahead"

        # High uncertainty → conservative
        if uncertainty_high:
            return "RISKY", "high motion uncertainty"

        # Planning risk already high → block overtaking
        if risk_level == "HIGH":
            return "NOT ADVISED", "high risk level"

        # Lead vehicle not slower → no need to overtake
        if relative_speed <= 0:
            return "NOT ADVISED", "lead vehicle not slower"

        # All checks passed → safe opportunity
        return "SAFE", "clear adjacent lane and slower lead vehicle"
