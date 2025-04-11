import os
import json

MODEL_DIR = "models"
VERSION_FILE = os.path.join(MODEL_DIR, "model_versions.json")

def get_next_model_version() -> int:
    os.makedirs(MODEL_DIR, exist_ok=True)

    if not os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "w") as f:
            json.dump({"latest_version": 0, "versions": []}, f)

    with open(VERSION_FILE, "r") as f:
        version_data = json.load(f)

    next_version = version_data["latest_version"] + 1
    version_data["latest_version"] = next_version
    version_data["versions"].append(f"anomaly_model_v{next_version}.pkl")

    with open(VERSION_FILE, "w") as f:
        json.dump(version_data, f)

    return next_version
