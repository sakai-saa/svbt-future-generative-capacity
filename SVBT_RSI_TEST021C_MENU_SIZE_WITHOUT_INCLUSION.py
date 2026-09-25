# SVBT_RSI_TEST021C_MENU_SIZE_WITHOUT_INCLUSION.py

import os
import csv
from datetime import datetime
from openai import OpenAI

MODEL = "gpt-5.6-sol"
REASONING_EFFORT = "medium"
RUNS_PER_CONDITION = 10

OUTPUT_CSV = "SVBT_RSI_TEST021C_RESULTS.csv"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ============================================================
# PURPOSE
#
# Separate:
#
#   strict set inclusion
#
# from:
#
#   future menu size / number of remaining choices
#
# TEST021A:
#   {X,Y} vs {Y}
#   -> different size AND strict inclusion
#
# TEST021C:
#   {X,Y} vs {Z}
#   -> different size, NO set inclusion
#
# No utility.
# No UND.
# No NEXT.
# No Gamma.
# No QOV.
# No Future Loss Risk.
# No SVBT explanation.
# No ground truth.
# ============================================================

CONDITIONS = [
    {
        "condition": "NORMAL",
        "U0_future": "{X,Y}",
        "U1_future": "{Z}",
        "larger_menu_action": "U0",
    },
    {
        "condition": "SWAPPED",
        "U0_future": "{Z}",
        "U1_future": "{X,Y}",
        "larger_menu_action": "U1",
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

No utility values are specified for X, Y, or Z.

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
    print("SVBT RSI TEST021C")
    print("MENU SIZE WITHOUT SET INCLUSION")
    print("=" * 76)

    print(f"MODEL:                {MODEL}")
    print(f"REASONING EFFORT:     {REASONING_EFFORT}")
    print("GROUND TRUTH:         NONE")
    print("HISTORY:              NONE")
    print("EXAMPLES:             NONE")
    print("UTILITY:              UNSPECIFIED")
    print("UND:                  NONE")
    print("NEXT:                 NONE")
    print("GAMMA:                NONE")
    print("QOV:                  NONE")
    print("FUTURE LOSS RISK:     NONE")
    print("SVBT EXPLANATION:     NONE")
    print("REASON OUTPUT:        NONE")
    print(f"RUNS/CONDITION:       {RUNS_PER_CONDITION}")
    print()

    rows = []

    for condition in CONDITIONS:

        name = condition["condition"]
        larger_menu_action = condition["larger_menu_action"]

        print("-" * 76)
        print(f"CONDITION: {name}")
        print(f"LARGER MENU ACTION (LOCAL ONLY): {larger_menu_action}")
        print("-" * 76)

        prompt = build_prompt(condition)

        for run_number in range(1, RUNS_PER_CONDITION + 1):

            choice, raw = run_model(prompt)

            chose_larger_menu = (
                choice == larger_menu_action
                if choice != "INVALID"
                else False
            )

            print(
                f"{name:<8} "
                f"run={run_number:02d} "
                f"choice={choice:<7} "
                f"larger_menu={chose_larger_menu}"
            )

            rows.append({
                "timestamp": datetime.now().isoformat(),
                "test": "TEST021C",
                "model": MODEL,
                "reasoning_effort": REASONING_EFFORT,

                "condition": name,
                "run": run_number,

                "U0_future_set": condition["U0_future"],
                "U1_future_set": condition["U1_future"],

                # Local analysis only; not sent to model.
                "larger_menu_action": larger_menu_action,

                "model_choice": choice,
                "chose_larger_menu": chose_larger_menu,
                "raw_output": raw,

                "ground_truth": "NONE",
                "utility": "UNSPECIFIED",
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

    larger_count = sum(
        1 for r in valid_rows
        if r["chose_larger_menu"]
    )

    total = len(valid_rows)

    print()
    print("=" * 76)
    print("RESULT")
    print("=" * 76)

    print(f"VALID RUNS:           {total}")
    print(f"LARGER MENU CHOICES:  {larger_count}")

    if total:
        print(
            f"LARGER MENU RATE:     "
            f"{larger_count / total:.3f}"
        )

    print()
    print("BY CONDITION")

    for condition in CONDITIONS:

        name = condition["condition"]

        subset = [
            r for r in valid_rows
            if r["condition"] == name
        ]

        n_larger = sum(
            1 for r in subset
            if r["chose_larger_menu"]
        )

        rate = (
            n_larger / len(subset)
            if subset
            else 0.0
        )

        print(
            f"{name}: "
            f"{n_larger}/{len(subset)} "
            f"larger_menu_rate={rate:.3f}"
        )

    print()
    print(f"CSV SAVED: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()