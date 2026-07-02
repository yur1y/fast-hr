#!/usr/bin/env python3
import json
import os
import sys


def main():
    threshold = float(os.environ.get("CANARY_THRESHOLD", 0.15))
    log_path = os.environ.get("CANARY_LOG", "canary_output.json")

    if not os.path.exists(log_path):
        print("No canary log found")
        sys.exit(0)

    with open(log_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for candidate in data.get("candidates", []):
        diff = candidate.get("diff", 0)
        if diff > threshold:
            print(f"DRIFT: {candidate.get('id', '<unknown>')} diff={diff}")
            sys.exit(1)

    print("No drift detected")
    sys.exit(0)


if __name__ == "__main__":
    main()
