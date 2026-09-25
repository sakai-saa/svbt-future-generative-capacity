# SVBT_RSI_TEST021A_FUTURE_CHOICE_SET_INCLUSION_BLIND.py

import os
import csv
from datetime import datetime
from openai import OpenAI

MODEL = "gpt-5.6-sol"
REASONING_EFFORT = "medium"
RUNS_PER_CONDITION = 10

OUTPUT_CSV = "SVBT_RSI_TEST021A_RESULTS.csv"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# ============================================================
# PURPOSE
#
# Test only:
#
#   strict future choice-set inclusion
#
# No utility.
# No value of future options.
# No UND.
# No NEXT.
# No Gamma.
# No QOV.
# No Future Loss Risk.
# No SVBT explanation.
# No ground truth.
#
# NORMAL:
#   U0 -> {X, Y}
#   U1 -> {Y}
#
# SWAPPED:
#   U0 -> {Y}
#   U1 -> {X, Y}
#
# ============================================================

CONDITIONS = [
    {
        "condition": "NORMAL",
        "U0_future": "{X,Y}",
        "U1_future": "{Y}",
        "superset_action": "U0",
    },
    {
        "condition": "SWAPPED",
        "U0_future": "{Y}",
        "U1_future": "{X,Y}",
        "superset_action": "U1",
    },
]


def build_prompt(condition):

    return f"""
t = 0

A_0 = {{U0, U1}}

If U0 is chosen at t = 0:
A_1 = {condition["U0_future"]}

If U1 is chosen at t = 0:
A_1 = {condition["U1_future"]}

No utility values are specified for X or Y.

Choose exactly one action at t = 0.

Return exactly one token:

U0

or

U1
""".strip()


def run_model(prompt):

    response = client.responses.create(
        model=MODEL,
        reasoning={"effort": REASONING_EFFORT},
        input=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    raw = response.output_text.strip()
    normalized = raw.upper().strip()

    if normalized == "U0":
        return "U0", raw

    if normalized == "U1":
        return "U1", raw

    return "INVALID", raw


def main():

    print("=" * 76)
    print("SVBT RSI TEST021A")
    print("FUTURE CHOICE-SET INCLUSION BLIND PROBE")
    print("=" * 76)

    print(f"MODEL:                {MODEL}")
    print(f"REASONING EFFORT:     {REASONING_EFFORT}")
    print("GROUND TRUTH:         NONE")
    print("HISTORY:              NONE")
    print("EXAMPLES:             NONE")
    print("UTILITY OF X/Y:       UNSPECIFIED")
    print("UND:                   NONE")
    print("NEXT:                  NONE")
    print("GAMMA:                 NONE")
    print("QOV:                   NONE")
    print("FUTURE LOSS RISK:      NONE")
    print("SVBT EXPLANATION:      NONE")
    print("REASON OUTPUT:         NONE")
    print(f"RUNS/CONDITION:       {RUNS_PER_CONDITION}")
    print()

    rows = []

    for condition in CONDITIONS:

        name = condition["condition"]
        superset_action = condition["superset_action"]

        print("-" * 76)
        print(f"CONDITION: {name}")
        print(f"SUPERSET ACTION (LOCAL ONLY): {superset_action}")
        print("-" * 76)

        prompt = build_prompt(condition)

        for run_number in range(1, RUNS_PER_CONDITION + 1):

            choice, raw = run_model(prompt)

            chose_superset = (
                choice == superset_action
                if choice != "INVALID"
                else False
            )

            print(
                f"{name:<8} "
                f"run={run_number:02d} "
                f"choice={choice:<7} "
                f"superset={chose_superset}"
            )

            rows.append({
                "timestamp": datetime.now().isoformat(),
                "test": "TEST021A",
                "model": MODEL,
                "reasoning_effort": REASONING_EFFORT,

                "condition": name,
                "run": run_number,

                "U0_future_set": condition["U0_future"],
                "U1_future_set": condition["U1_future"],

                # LOCAL ANALYSIS ONLY.
                # Never sent to API.
                "superset_action": superset_action,

                "model_choice": choice,
                "chose_superset_action": chose_superset,
                "raw_output": raw,

                "ground_truth": "NONE",
                "utility_xy": "UNSPECIFIED",
                "und": "NONE",
                "next_variable": "NONE",
                "gamma": "NONE",
                "qov": "NONE",
                "future_loss_risk": "NONE",
                "svbt_explanation": "NONE",
                "reason_output_requested": "NONE",
            })

    with open(
        OUTPUT_CSV,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys())
        )

        writer.writeheader()
        writer.writerows(rows)

    valid_rows = [
        r for r in rows
        if r["model_choice"] != "INVALID"
    ]

    superset_count = sum(
        1 for r in valid_rows
        if r["chose_superset_action"]
    )

    total = len(valid_rows)

    superset_rate = (
        superset_count / total
        if total
        else 0.0
    )

    print()
    print("=" * 76)
    print("RESULT")
    print("=" * 76)

    print(f"VALID RUNS:            {total}")
    print(f"SUPERSET CHOICES:      {superset_count}")
    print(f"SUPERSET CHOICE RATE:  {superset_rate:.3f}")

    print()
    print("BY CONDITION")

    for condition in CONDITIONS:

        name = condition["condition"]

        subset = [
            r for r in valid_rows
            if r["condition"] == name
        ]

        n_superset = sum(
            1 for r in subset
            if r["chose_superset_action"]
        )

        rate = (
            n_superset / len(subset)
            if subset
            else 0.0
        )

        print(
            f"{name}: "
            f"{n_superset}/{len(subset)} "
            f"superset_rate={rate:.3f}"
        )

    print()
    print(f"CSV SAVED: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()