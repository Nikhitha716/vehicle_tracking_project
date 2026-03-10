# boxmot/boxmot/addons/lane_validation/lane_logger.py

import csv
from pathlib import Path


class LaneEventLogger:
    def __init__(self, save_dir):
        self.csv_path = Path(save_dir) / "lane_validation_log.csv"
        self.initialized = False

    def log(self, frame, track_id, prev_lane, curr_lane, event_type):
        if not self.initialized:
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["frame", "track_id", "prev_lane", "curr_lane", "event"]
                )
            self.initialized = True

        with open(self.csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [frame, track_id, prev_lane, curr_lane, event_type]
            )
