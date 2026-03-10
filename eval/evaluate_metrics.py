import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs", "occlusion_log.json")

with open(LOG_FILE, "r") as f:
    logs = json.load(f)

# ---------- Containers ----------
total_ids = set()
occluded_ids = set()
recovered_ids = set()

id_switches = 0
total_events = 0

# track_id -> last known status
last_status = {}

# ---------- Process logs ----------
for entry in logs:
    frame = entry["frame"]
    tid = entry["track_id"]
    status = entry["status"]  # visible / occluded / reappeared

    total_ids.add(tid)
    total_events += 1

    if status == "occluded":
        occluded_ids.add(tid)

    if status == "reappeared":
        recovered_ids.add(tid)

        # If same vehicle was occluded before and came back as new ID
        if last_status.get(tid) == "occluded":
            id_switches += 1

    last_status[tid] = status

# ---------- Metrics ----------
true_recoveries = recovered_ids.intersection(occluded_ids)
occlusion_recovery_rate = len(true_recoveries) / max(len(occluded_ids), 1)

id_switch_rate = id_switches / max(len(total_ids), 1)

# ---------- Output ----------
print("\nEvaluation Metrics")
print("------------------")
print(f"Total Track IDs        : {len(total_ids)}")
print(f"Occluded IDs           : {len(occluded_ids)}")
print(f"Recovered IDs          : {len(recovered_ids)}")
print(f"Occlusion Recovery Rate: {occlusion_recovery_rate:.2f}")
print(f"ID Switch Rate         : {id_switch_rate:.2f}")

