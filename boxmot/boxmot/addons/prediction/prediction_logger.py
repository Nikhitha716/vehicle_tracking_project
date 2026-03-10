# boxmot/boxmot/addons/prediction/prediction_logger.py

import csv
from pathlib import Path


class PredictionLogger:
    """
    Logs uncertainty-aware behavior predictions.
    """

    def __init__(self, save_dir):
        self.csv_path = Path(save_dir) / "prediction_log.csv"
        self.initialized = False

    def log(self, frame, track_id, probs):
        """
        Log prediction probabilities.

        Args:
            frame (int)
            track_id (int)
            probs (dict): behavior -> probability
        """
        if not self.initialized:
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["frame", "track_id"] + list(probs.keys())
                )
            self.initialized = True

        with open(self.csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [frame, track_id] + [round(v, 3) for v in probs.values()]
            )

        # Terminal summary (clean, one line)
        summary = ", ".join(
            f"{k}:{v:.2f}" for k, v in probs.items()
        )
        print(
            f"[Prediction] Frame {frame} | ID {track_id} | {summary}"
        )
