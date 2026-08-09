import pandas as pd
from pathlib import Path

from src.pricing_model import (
    assign_tiers,
    calculate_saas_metrics,
)

from src.churn_model import (
    estimate_churn_probability,
    calculate_retention_metrics,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "synthetic_customers.csv"
)


def run_pricing_scenarios(
    customers,
    professional_prices=None,
    practice_prices=None,
):
    """
    Test multiple SaaS pricing combinations and calculate
    acquisition, churn, and retained-revenue outcomes.
    """

    if professional_prices is None:
        professional_prices = [29, 39, 49, 59, 69, 79]

    if practice_prices is None:
        practice_prices = [99, 119, 129, 149, 169, 189]

    results = []

    for professional_price in professional_prices:
        for practice_price in practice_prices:

            # Assign customers to Free, Professional, or Practice
            # based on the current pricing scenario.
            priced_customers = assign_tiers(
                customers,
                professional_price=professional_price,
                practice_price=practice_price,
            )

            # Estimate churn probability for paying customers.
            priced_customers = estimate_churn_probability(
                priced_customers
            )

            # Initial SaaS metrics.
            pricing_metrics = calculate_saas_metrics(
                priced_customers
            )

            # Expected retained revenue after modeled churn.
            retention_metrics = calculate_retention_metrics(
                priced_customers
            )

            tier_counts = pricing_metrics["tier_counts"]

            results.append(
                {
                    "professional_price": professional_price,
                    "practice_price": practice_price,

                    "free_customers":
                        tier_counts.get("Free", 0),

                    "professional_customers":
                        tier_counts.get("Professional", 0),

                    "practice_customers":
                        tier_counts.get("Practice", 0),

                    "paid_conversion_rate":
                        pricing_metrics[
                            "paid_conversion_rate"
                        ],

                    "monthly_churn":
                        retention_metrics[
                            "average_monthly_churn"
                        ],

                    "initial_mrr":
                        pricing_metrics["mrr"],

                    "initial_arr":
                        pricing_metrics["arr"],

                    "retained_mrr":
                        retention_metrics[
                            "retained_mrr"
                        ],

                    "retained_arr":
                        retention_metrics[
                            "retained_arr"
                        ],

                    "arpu":
                        pricing_metrics["arpu"],
                }
            )

    return pd.DataFrame(results)


def find_best_scenario(results):
    """
    Find the pricing combination with the highest
    expected retained monthly recurring revenue.
    """

    best = results.loc[
        results["retained_mrr"].idxmax()
    ]

    return best


def print_results(results, best):
    """
    Print the full pricing scenario comparison and
    the best retained-revenue scenario.
    """

    display = results.copy()

    display["paid_conversion_rate"] = (
        display["paid_conversion_rate"] * 100
    ).round(2)

    display["monthly_churn"] = (
        display["monthly_churn"] * 100
    ).round(2)

    display["initial_mrr"] = (
        display["initial_mrr"].round(2)
    )

    display["retained_mrr"] = (
        display["retained_mrr"].round(2)
    )

    display["arpu"] = (
        display["arpu"].round(2)
    )

    print("\n" + "=" * 90)
    print("HEALTHCARE SAAS PRICING + RETENTION ANALYSIS")
    print("=" * 90)

    print("\n")

    print(
        display[
            [
                "professional_price",
                "practice_price",
                "paid_conversion_rate",
                "monthly_churn",
                "initial_mrr",
                "retained_mrr",
                "arpu",
            ]
        ].to_string(index=False)
    )

    print("\n" + "-" * 90)
    print("BEST RETAINED REVENUE SCENARIO")
    print("-" * 90)

    print(
        f"Professional price: "
        f"${best['professional_price']:.0f}"
    )

    print(
        f"Practice price: "
        f"${best['practice_price']:.0f}"
    )

    print(
        f"Paid conversion rate: "
        f"{best['paid_conversion_rate']:.2%}"
    )

    print(
        f"Average monthly churn: "
        f"{best['monthly_churn']:.2%}"
    )

    print(
        f"Initial MRR: "
        f"${best['initial_mrr']:,.2f}"
    )

    print(
        f"Expected retained MRR: "
        f"${best['retained_mrr']:,.2f}"
    )

    print(
        f"Expected retained ARR: "
        f"${best['retained_arr']:,.2f}"
    )

    print(
        f"ARPU: "
        f"${best['arpu']:,.2f}"
    )


if __name__ == "__main__":

    customers = pd.read_csv(
        DATA_PATH
    )

    results = run_pricing_scenarios(
        customers
    )

    best = find_best_scenario(
        results
    )

    print_results(
        results,
        best
    )