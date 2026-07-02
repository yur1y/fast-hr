#!/usr/bin/env python3
import asyncio
import os


async def main():
    from app.services.fuzzer import FuzzerEngine

    engine = FuzzerEngine()
    lie_types = os.environ.get("FUZZER_LIE_TYPES", "date_overlap,skill_inflation")
    count = int(os.environ.get("FUZZER_COUNT", "10"))

    lie_types_list = [t.strip() for t in lie_types.split(",")]
    result = await engine.run(lie_types=lie_types_list, count=count)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
