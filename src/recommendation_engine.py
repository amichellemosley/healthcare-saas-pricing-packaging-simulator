import pandas as pd
from pathlib import Path

from src.packaging_engine import (
    PACKAGE_STRATEGIES,
    assign_tiers_with_packaging,
)

from src.pricing_model import (
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


PROFESSIONAL_PRICES = [
    29,
    39,
    49,
    59,
    69,
    79,
]

PRACTICE_PRICES = [
    99,
    119,
    129,
    149,
    169,
    189,
]


def run_full_pricing_packaging_analysis(
    customers,
):
    """
    Test every packaging strategy against every
    Professional and Practice price combination.
    """

    results = []

    for (
        strategy_name,
        strategy,
    ) in PACKAGE_STRATEGIES.items():

        for professional_price in PROFESSIONAL_PRICES:

            for practice_price in PRACTICE_PRICES:

                priced = assign_tiers_with_packaging(
                    customers,
                    professional_features=
                        strategy["professional_features"],
                    practice_features=
                        strategy["practice_features"],
                    professional_price=
                        professional_price,
                    practice_price=
                        practice_price,
                )

                priced = estimate_churn_probability(
                    priced
                )

                pricing_metrics = calculate_saas_metrics(
                    priced
                )

                retention_metrics = calculate_retention_metrics(
                    priced
                )

                tier_counts = pricing_metrics["tier_counts"]

                results.append(
                    {
                        "strategy":
                            strategy_name,

                        "professional_price":
                            professional_price,

                        "practice_price":
                            practice_price,

                        "professional_features":
                            ", ".join(
                                strategy[
                                    "professional_features"
                                ]
                            ),

                        "practice_only_features":
                            ", ".join(
                                strategy[
                                    "practice_features"
                                ]
                            ),

                        "free_customers":
                            tier_counts.get(
                                "Free",
                                0,
                            ),

                        "professional_customers":
                            tier_counts.get(
                                "Professional",
                                0,
                            ),

                        "practice_customers":
                            tier_counts.get(
                                "Practice",
                                0,
                            ),

                        "paid_conversion_rate":
                            pricing_metrics[
                                "paid_conversion_rate"
                            ],

                        "monthly_churn":
                            retention_metrics[
                                "average_monthly_churn"
                            ],

                        "initial_mrr":
                            pricing_metrics[
                                "mrr"
                            ],

                        "retained_mrr":
                            retention_metrics[
                                "retained_mrr"
                            ],

                        "retained_arr":
                            retention_metrics[
                                "retained_arr"
                            ],

                        "arpu":
                            pricing_metrics[
                                "arpu"
                            ],
                    }
                )

    return pd.DataFrame(
        results
    )


def find_best_strategy(
    results,
):
    """
    Select the strategy with the highest expected
    retained monthly recurring revenue.
    """

    return results.loc[
        results["retained_mrr"].idxmax()
    ]


def print_recommendation(
    best,
):
    """
    Print the final SaaS pricing and packaging recommendation.
    """

    print(
        "\n" + "=" * 80
    )

    print(
        "FINAL HEALTHCARE SAAS PRICING + PACKAGING RECOMMENDATION"
    )

    print(
        "=" * 80
    )

    print(
        f"\nPackage strategy: "
        f"{best['strategy']}"
    )

    print(
        f"\nProfessional price: "
        f"${best['professional_price']:.0f}/month"
    )

    print(
        f"Practice price: "
        f"${best['practice_price']:.0f}/month"
    )

    print(
        f"\nProfessional includes: "
        f"{best['professional_features']}"
    )

    print(
        f"Practice additionally includes: "
        f"{best['practice_only_features']}"
    )

    print(
        f"\nPaid conversion rate: "
        f"{best['paid_conversion_rate']:.2%}"
    )

    print(
        f"Expected monthly churn: "
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

    results = run_full_pricing_packaging_analysis(
        customers
    )

    best = find_best_strategy(
        results
    )

    print_recommendation(
        best
    )