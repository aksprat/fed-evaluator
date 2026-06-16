import argparse
import asyncio
import json
import os
import time

from inference.classifier import classify_issue

DEFAULT_CONCURRENCY = int(
    os.getenv("CONCURRENCY", "10")
)


async def classify_one_issue(
    issue,
    model,
    semaphore
):

    async with semaphore:

        result = await asyncio.to_thread(
            classify_issue,
            issue,
            model
        )

        return result


async def run_model(
    model,
    concurrency
):

    with open("data/issues_snapshot.json") as f:
        issues = json.load(f)

    semaphore = asyncio.Semaphore(concurrency)

    start_time = time.perf_counter()

    tasks = [

        classify_one_issue(
            issue,
            model,
            semaphore
        )

        for issue in issues
    ]

    results = await asyncio.gather(*tasks)

    wall_clock_time = time.perf_counter() - start_time

    throughput = len(issues) / wall_clock_time

    output = {
        "model": model,
        "concurrency": concurrency,
        "wall_clock_seconds": wall_clock_time,
        "throughput_rps": throughput,
        "results": results
    }

    os.makedirs("results", exist_ok=True)

    output_file = f"results/{model}.json"

    with open(output_file, "w") as f:

        json.dump(
            output,
            f,
            indent=2
        )

    print()

    print("======================================")
    print("Model:", model)
    print("Concurrency:", concurrency)
    print("Issues:", len(issues))
    print("Wall clock:", round(wall_clock_time, 2), "seconds")
    print("Throughput:", round(throughput, 2), "req/sec")
    print("Saved to:", output_file)
    print("======================================")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        required=True
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY
    )

    args = parser.parse_args()

    asyncio.run(

        run_model(
            args.model,
            args.concurrency
        )

    )
