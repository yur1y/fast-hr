#!/usr/bin/env python3
import os
import json


def main():
    from app.clients.observability_factory import observability

    dataset_name = os.environ.get("LANGFUSE_DATASET", "adversarial-tests")
    output_path = os.environ.get("OUTPUT_PATH", "data/adversarial/dataset_export.json")

    try:
        if hasattr(observability, "client"):
            dataset = observability.client.get_dataset(dataset_name)
            items = list(dataset.items)
            with open(output_path, "w") as f:
                json.dump([item.input for item in items], f)
            print(f"Exported {len(items)} items to {output_path}")
        else:
            print("Observability provider does not support dataset export")
    except Exception as exc:
        print(f"Failed to pull dataset: {exc}")
        raise


if __name__ == "__main__":
    main()