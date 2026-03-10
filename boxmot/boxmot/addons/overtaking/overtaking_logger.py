# boxmot/boxmot/addons/overtaking/overtaking_logger.py

import csv
from pathlib import Path


class OvertakingLogger:
    """
    Logs overtaking opportunity assessment results.
    """

    def __init__(self, save_dir):
        self.csv_path = Path(save_dir) / "overtaking_log.csv"
        self.initialized = False

    def log(self, frame, track_id, lane_id, state, reason):
        """
        Log overtaking decision.

        Args:
            frame (int)
            track_id (int)
            lane_id (int)
            state (str): SAFE / RISKY / NOT ADVISED
            reason (str)
        """
        if not self.initialized:
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["frame", "track_id", "lane_id", "overtake_state", "reason"]
                )
            self.initialized = True

        with open(self.csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [frame, track_id, lane_id, state, reason]
            )

        # Terminal output (clean, informative)
        print(
            f"[Overtake] Frame {frame} | ID {track_id} | Lane {lane_id} | "
            f"{state} | reason: {reason}"
        )
