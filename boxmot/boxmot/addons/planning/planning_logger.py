# boxmot/boxmot/addons/planning/planning_logger.py

import csv
from pathlib import Path


class PlanningLogger:
    """
    Logs risk-sensitive advisory planning outputs.
    """

    def __init__(self, save_dir):
        self.csv_path = Path(save_dir) / "planning_log.csv"
        self.initialized = False

    def log(self, frame, track_id, risk_level, advisory):
        """
        Log planning decision.

        Args:
            frame (int)
            track_id (int)
            risk_level (str)
            advisory (str)
        """
        if not self.initialized:
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["frame", "track_id", "risk_level", "advisory"]
                )
            self.initialized = True

        with open(self.csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [frame, track_id, risk_level, advisory]
            )

        # Terminal output (clean, advisory style)
        print(
            f"[Planning] Frame {frame} | ID {track_id} | Risk: {risk_level} | Advice: {advisory}"
        )
