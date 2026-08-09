import pandas as pd
import numpy as np
from pathlib import Path

from src.pricing_model import (
    calculate_saas_metrics,
    sigmoid,
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

RANDOM_SEED = 100

PROFESSIONAL_PRICE = 49
PRACTICE_PRICE = 119


# ---------------------------------------------------------
# PACKAGE CONFIGURATIONS
# ---------------------------------------------------------

PACKAGE_STRATEGIES = {

    "Core Professional": {
        "professional_features": [
            "scheduling",
            "communication",
        ],
        "practice_features": [
            "analytics",
            "claims",
            "management",
        ],
    },

    "Analytics Professional": {
        "professional_features": [
            "scheduling",
            "communication",
            "analytics",
        ],
        "practice_features": [
            "claims",
            "management",
        ],
    },

    "Claims Professional": {
        "professional_features": [
            "scheduling",
            "communication",
            "claims",
        ],
        "practice_features": [
            "analytics",
            "management",
        ],
    },

    "Expanded Professional": {
        "professional_features": [
            "scheduling",
            "communication",
            "analytics",
            "claims",
        ],
        "practice_features": [
            "management",
        ],
    },
}


FEATURE_COLUMNS = {
    "scheduling": "scheduling_need",
    "communication": "patient_communication_need",
    "analytics": "analytics_need",
    "claims": "claims_automation_need",
    "management": "practice_management_need",
}


def calculate_package_fit(
    df,
    features,
):
    """
    Calculate how strongly a package matches each
    customer's feature needs.
    """

    feature_columns = [
        FEATURE_COLUMNS[feature]
        for feature in features
    ]

    return df[
        feature_columns
    ].mean(axis=1)


def assign_tiers_with_packaging(
    df,
    professional_features,
    practice_features,
    professional_price=PROFESSIONAL_PRICE,
    practice_price=PRACTICE_PRICE,
):
    """
    Simulate customer tier selection for a specific
    SaaS packaging strategy.
    """

    df = df.copy()

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    # Professional package value
    df["professional_feature_fit"] = (
        calculate_package_fit(
            df,
            professional_features,
        )
    )

    # Practice includes Professional features plus
    # the additional Practice-only features.
    all_practice_features = list(
        dict.fromkeys(
            professional_features
            + practice_features
        )
    )

    df["practice_feature_fit"] = (
        calculate_package_fit(
            df,
            all_practice_features,
        )
    )

    # Give larger practices additional value from
    # the Practice tier.
    df["practice_feature_fit"] = (
        df["practice_feature_fit"] * 0.90
        + np.clip(
            df["practice_size"] / 20,
            0,
            1,
        ) * 0.10
    )

    # -----------------------------------------------------
    # PROFESSIONAL CONVERSION
    # -----------------------------------------------------

    professional_price_value = (
        df["willingness_to_pay"]
        - professional_price
    ) / 20

    professional_score = (
        -2.0
        + professional_price_value
        + 1.5
        * df["professional_feature_fit"]
        - 1.5
        * df["price_sensitivity"]
    )

    df[
        "professional_conversion_probability"
    ] = sigmoid(
        professional_score
    )

    # -----------------------------------------------------
    # PRACTICE CONVERSION
    # -----------------------------------------------------

    practice_price_value = (
        df["willingness_to_pay"]
        - practice_price
    ) / 30

    practice_score = (
        -2.5
        + practice_price_value
        + 2.0
        * df["practice_feature_fit"]
        - 1.2
        * df["price_sensitivity"]
        + 0.04
        * df["practice_size"]
    )

    df[
        "practice_conversion_probability"
    ] = sigmoid(
        practice_score
    )

    # Solo providers cannot purchase Practice.
    df.loc[
        df["practice_size"] == 1,
        "practice_conversion_probability",
    ] = 0

    # -----------------------------------------------------
    # PURCHASE SIMULATION
    # -----------------------------------------------------

    df["selected_tier"] = "Free"

    professional_draw = rng.random(
        len(df)
    )

    practice_draw = rng.random(
        len(df)
    )

    professional_purchase = (
        professional_draw
        < df[
            "professional_conversion_probability"
        ]
    )

    practice_purchase = (
        practice_draw
        < df[
            "practice_conversion_probability"
        ]
    )

    df.loc[
        professional_purchase,
        "selected_tier",
    ] = "Professional"

    df.loc[
        practice_purchase,
        "selected_tier",
    ] = "Practice"

    # -----------------------------------------------------
    # REVENUE
    # -----------------------------------------------------

    df["monthly_price"] = 0

    df.loc[
        df["selected_tier"] == "Professional",
        "monthly_price",
    ] = professional_price

    df.loc[
        df["selected_tier"] == "Practice",
        "monthly_price",
    ] = practice_price

    return df


def evaluate_strategy(
    customers,
    strategy_name,
    strategy,
):
    """
    Evaluate conversion, churn, and revenue for
    one packaging strategy.
    """

    priced = assign_tiers_with_packaging(
        customers,
        strategy[
            "professional_features"
        ],
        strategy[
            "practice_features"
        ],
    )

    priced = estimate_churn_probability(
        priced
    )

    pricing_metrics = (
        calculate_saas_metrics(
            priced
        )
    )

    retention_metrics = (
        calculate_retention_metrics(
            priced
        )
    )

    counts = pricing_metrics[
        "tier_counts"
    ]

    return {

        "strategy":
            strategy_name,

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
            counts.get("Free", 0),

        "professional_customers":
            counts.get(
                "Professional",
                0,
            ),

        "practice_customers":
            counts.get(
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
            pricing_metrics["mrr"],

        "retained_mrr":
            retention_metrics[
                "retained_mrr"
            ],

        "arpu":
            pricing_metrics["arpu"],
    }


def run_packaging_analysis(
    customers,
):

    results = []

    for (
        strategy_name,
        strategy,
    ) in PACKAGE_STRATEGIES.items():

        result = evaluate_strategy(
            customers,
            strategy_name,
            strategy,
        )

        results.append(
            result
        )

    return pd.DataFrame(
        results
    )


if __name__ == "__main__":

    customers = pd.read_csv(
        DATA_PATH
    )

    results = (
        run_packaging_analysis(
            customers
        )
    )

    display = results.copy()

    display[
        "paid_conversion_rate"
    ] = (
        display[
            "paid_conversion_rate"
        ]
        * 100
    ).round(2)

    display[
        "monthly_churn"
    ] = (
        display[
            "monthly_churn"
        ]
        * 100
    ).round(2)

    display[
        "initial_mrr"
    ] = (
        display[
            "initial_mrr"
        ].round(2)
    )

    display[
        "retained_mrr"
    ] = (
        display[
            "retained_mrr"
        ].round(2)
    )

    display["arpu"] = (
        display["arpu"].round(2)
    )

    print(
        "\n## SAAS PACKAGING ANALYSIS\n"
    )

    print(
        display[
            [
                "strategy",
                "paid_conversion_rate",
                "monthly_churn",
                "initial_mrr",
                "retained_mrr",
                "arpu",
            ]
        ].to_string(
            index=False
        )
    )

    best = results.loc[
        results[
            "retained_mrr"
        ].idxmax()
    ]

    print(
        "\n## RECOMMENDED PACKAGE\n"
    )

    print(
        f"Strategy: "
        f"{best['strategy']}"
    )

    print(
        f"Professional includes: "
        f"{best['professional_features']}"
    )

    print(
        f"Practice additionally includes: "
        f"{best['practice_only_features']}"
    )

    print(
        f"Paid conversion: "
        f"{best['paid_conversion_rate']:.2%}"
    )

    print(
        f"Monthly churn: "
        f"{best['monthly_churn']:.2%}"
    )

    print(
        f"Expected retained MRR: "
        f"${best['retained_mrr']:,.2f}"
    )

    print(
        f"ARPU: "
        f"${best['arpu']:,.2f}"
    )