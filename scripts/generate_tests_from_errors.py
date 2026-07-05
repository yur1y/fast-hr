#!/usr/bin/env python3
import json
import os


def main():
    input_path = os.environ.get("TP_INPUT_PATH", os.environ.get("INPUT_PATH", "data/adversarial/dataset_export.json"))
    output_path = os.environ.get("TP_OUTPUT_PATH", os.environ.get("OUTPUT_PATH", "tests/generated/test_adversarial_errors.py"))

    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return

    with open(input_path) as f:
        items = json.load(f)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    lines = [
        "import pytest",
        "from httpx import AsyncClient, ASGITransport",
        "from app.main import app",
        "",
        "",
        "@pytest.mark.asyncio",
    ]

    for i, item in enumerate(items):
        test_name = f"test_adversarial_case_{i + 1}"
        body = json.dumps(item)
        lines.extend(
            [
                f"async def {test_name}():",
                f'    transport = ASGITransport(app=app)',
                f'    async with AsyncClient(transport=transport, base_url="http://test") as ac:',
                f'        resp = await ac.post("/api/v1/screenings", json={body})',
                f'    assert resp.status_code in (200, 422)',
                "",
            ]
        )

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Generated {len(items)} test cases -> {output_path}")


if __name__ == "__main__":
    main()
