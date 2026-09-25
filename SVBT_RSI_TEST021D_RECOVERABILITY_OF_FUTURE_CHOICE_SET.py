# SVBT_RSI_TEST021D_RECOVERABILITY_OF_FUTURE_CHOICE_SET.py

import os
import csv
from datetime import datetime
from openai import OpenAI

MODEL = "gpt-5.6-sol"
REASONING_EFFORT = "medium"
RUNS_PER_CONDITION = 10

OUTPUT_CSV = "SVBT_RSI_TEST021D_RESULTS.csv"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# ============================================================
# PURPOSE
#
# Test whether the choice effect seen in TEST021A depends on
# irreversible loss of the larger future choice set.
#
# IRREVERSIBLE:
#   smaller future set cannot later recover X.
#
# RECOVERABLE:
#   smaller future set can later recover X before terminal choice.
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
        "condition": "IRREV_NORMAL",
        "U0_future": "{X,Y}",
        "U1_future": "{Y}",
        "recoverable_action": None,
        "large_action": "U0",
    },
    {
        "condition": "IRREV_SWAPPED",
        "U0_future": "{Y}",
        "U1_future": "{X,Y}",
        "recoverable_action": None,
        "large_action": "U1",
    },
    {
        "condition": "RECOVER_NORMAL",
        "U0_future": "{X,Y}",
        "U1_future": "{Y}",
        "recoverable_action": "U1",
        "large_action": "U0",
    },
    {
        "condition": "RECOVER_SWAPPED",
        "U0_future": "{Y}",
        "U1_future": "{X,Y}",
        "recoverable_action": "U0",
        "large_action": "U1",
    },
]


def build_prompt(condition):

    recovery_text = ""

    if condition["recoverable_action"] is not None:
        a = condition["recoverable_action"]

        recovery_text = f"""

If {a} is chosen at t = 0, X is not available at t = 1.
However, before the terminal choice is made, X can be restored.
After restoration, the available terminal actions are {{X,Y}}.

No utility or cost is specified for restoration.
"""
    else:
        # Find the action with the smaller set
        if condition["U0_future"] == "{Y}":
            small_action = "U0"
        else:
            small_action = "U1"

        recovery_text = f"""

If {small_action} is chosen at t = 0, X is unavailable at t = 1
and cannot become available at any later step.
"""

    return f"""
t = 0

A_0 = {{U0, U1}}

If U0 is chosen at t = 0:
A_1 = {condition["U0_future"]}

If U1 is chosen at t = 0:
A_1 = {condition["U1_future"]}
{recovery_text}

No utility values are specified for X or Y.
No utility difference is specified between U0 and U1.

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
    print("SVBT RSI TEST021D")
    print("RECOVERABILITY OF FUTURE CHOICE-SET")
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
        large_action = condition["large_action"]

        print("-" * 76)
        print(f"CONDITION: {name}")
        print(f"LARGE-SET ACTION (LOCAL ONLY): {large_action}")
        print(
            "RECOVERABILITY: "
            + ("YES" if condition["recoverable_action"] else "NO")
        )
        print("-" * 76)

        prompt = build_prompt(condition)

        for run_number in range(1, RUNS_PER_CONDITION + 1):

            choice, raw = run_model(prompt)

            chose_large = (
                choice == large_action
                if choice != "INVALID"
                else False
            )

            print(
                f"{name:<16} "
                f"run={run_number:02d} "
                f"choice={choice:<7} "
                f"large_now={chose_large}"
            )

            rows.append({
                "timestamp": datetime.now().isoformat(),
                "test": "TEST021D",
                "model": MODEL,
                "reasoning_effort": REASONING_EFFORT,

                "condition": name,
                "run": run_number,

                "U0_future_set": condition["U0_future"],
                "U1_future_set": condition["U1_future"],
                "recoverable_action":
                    condition["recoverable_action"] or "NONE",

                # Local analysis only
                "large_action": large_action,

                "model_choice": choice,
                "chose_large_immediate_set": chose_large,
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

    print()
    print("=" * 76)
    print("RESULT")
    print("=" * 76)

    for condition in CONDITIONS:

        name = condition["condition"]

        subset = [
            r for r in valid_rows
            if r["condition"] == name
        ]

        n_large = sum(
            1 for r in subset
            if r["chose_large_immediate_set"]
        )

        rate = (
            n_large / len(subset)
            if subset
            else 0.0
        )

        print(
            f"{name:<16}: "
            f"large_now={n_large}/{len(subset)} "
            f"rate={rate:.3f}"
        )

    print()
    print(f"CSV SAVED: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()