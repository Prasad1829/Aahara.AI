import argparse
import json
import os
import sys


CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from evaluation.evaluator import SystemEvaluator


def main():
    parser = argparse.ArgumentParser(description="Evaluate Ingredient Based Recipe Intelligent System")
    parser.add_argument(
        "--benchmark",
        default=os.path.join("evaluation", "data", "benchmark_cases.json"),
        help="Path to benchmark json file",
    )
    parser.add_argument(
        "--max-cases",
        default=200,
        type=int,
        help="Maximum number of evaluation cases",
    )
    args = parser.parse_args()

    evaluator = SystemEvaluator(benchmark_path=args.benchmark, max_cases=args.max_cases)
    results = evaluator.run()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
