import pandas as pd
import numpy as np
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "synthetic_customers.csv"

PROFESSIONAL_PRICE = 49
PRACTICE_PRICE = 129

RANDOM_SEED = 100


def calculate_tier_values(df):
    """
    Calculate how well each SaaS package fits each customer's needs.
    """

    df = df.copy()

    df["professional_feature_fit"] = (
        df["scheduling_need"] * 0.35
        + df["patient_communication_need"] * 0.35
        + df["analytics_need"] * 0.30
    )

    df["practice_feature_fit"] = (
        df["analytics_need"] * 0.20
        + df["claims_automation_need"] * 0.35
        + df["practice_management_need"] * 0.35
        + np.clip(df["practice_size"] / 20, 0, 1) * 0.10
    )

    return df


def sigmoid(x):
    """
    Convert a purchase score into a probability between 0 and 1.
    """

    return 1 / (1 + np.exp(-x))


def assign_tiers(
    df,
    professional_price=PROFESSIONAL_PRICE,
    practice_price=PRACTICE_PRICE,
):
    """
    Estimate purchase probability and assign customers
    to Free, Professional, or Practice.

    The random generator is restarted with the same seed
    for every pricing scenario so different prices are
    compared against the same simulated customer behavior.
    """

    df = calculate_tier_values(df)

    # Reinitialize the random generator for every scenario.
    # This creates a fair apples-to-apples pricing comparison.
    rng = np.random.default_rng(RANDOM_SEED)

    # -----------------------------------------------------
    # Professional purchase model
    # -----------------------------------------------------

    professional_price_value = (
        df["willingness_to_pay"] - professional_price
    ) / 20

    professional_score = (
        -2.0
        + professional_price_value
        + 1.5 * df["professional_feature_fit"]
        - 1.5 * df["price_sensitivity"]
    )

    df["professional_conversion_probability"] = sigmoid(
        professional_score
    )

    # -----------------------------------------------------
    # Practice purchase model
    # -----------------------------------------------------

    practice_price_value = (
        df["willingness_to_pay"] - practice_price
    ) / 30

    practice_score = (
        -2.5
        + practice_price_value
        + 2.0 * df["practice_feature_fit"]
        - 1.2 * df["price_sensitivity"]
        + 0.04 * df["practice_size"]
    )

    df["practice_conversion_probability"] = sigmoid(
        practice_score
    )

    # Solo providers cannot purchase the Practice tier.
    df.loc[
        df["practice_size"] == 1,
        "practice_conversion_probability"
    ] = 0

    # -----------------------------------------------------
    # Simulate customer purchase decisions
    # -----------------------------------------------------

    df["selected_tier"] = "Free"

    professional_draw = rng.random(len(df))
    practice_draw = rng.random(len(df))

    professional_purchase = (
        professional_draw
        < df["professional_conversion_probability"]
    )

    practice_purchase = (
        practice_draw
        < df["practice_conversion_probability"]
    )

    # Professional first.
    df.loc[
        professional_purchase,
        "selected_tier"
    ] = "Professional"

    # Practice overrides Professional when the customer
    # purchases the higher tier.
    df.loc[
        practice_purchase,
        "selected_tier"
    ] = "Practice"

    # -----------------------------------------------------
    # Revenue assignment
    # -----------------------------------------------------

    df["monthly_price"] = 0

    df.loc[
        df["selected_tier"] == "Professional",
        "monthly_price"
    ] = professional_price

    df.loc[
        df["selected_tier"] == "Practice",
        "monthly_price"
    ] = practice_price

    return df


def calculate_saas_metrics(df):
    """
    Calculate core SaaS pricing metrics.
    """

    total_customers = len(df)

    paid_customers = (
        df["selected_tier"] != "Free"
    ).sum()

    paid_conversion_rate = (
        paid_customers / total_customers
    )

    mrr = df["monthly_price"].sum()

    arr = mrr * 12

    arpu = (
        mrr / total_customers
        if total_customers > 0
        else 0
    )

    tier_counts = (
        df["selected_tier"]
        .value_counts()
    )

    return {
        "total_customers": total_customers,
        "paid_customers": paid_customers,
        "paid_conversion_rate": paid_conversion_rate,
        "mrr": mrr,
        "arr": arr,
        "arpu": arpu,
        "tier_counts": tier_counts,
    }


if __name__ == "__main__":

    customers = pd.read_csv(
        DATA_PATH
    )

    priced_customers = assign_tiers(
        customers,
        professional_price=PROFESSIONAL_PRICE,
        practice_price=PRACTICE_PRICE,
    )

    metrics = calculate_saas_metrics(
        priced_customers
    )

    print("\n## HEALTHCARE SAAS PRICING RESULTS\n")

    print(
        f"Professional price: "
        f"${PROFESSIONAL_PRICE}/month"
    )

    print(
        f"Practice price: "
        f"${PRACTICE_PRICE}/month"
    )

    print("\nCustomer distribution:")

    print(
        metrics["tier_counts"]
    )

    print(
        f"\nPaid conversion rate: "
        f"{metrics['paid_conversion_rate']:.2%}"
    )

    print(
        f"MRR: "
        f"${metrics['mrr']:,.2f}"
    )

    print(
        f"ARR: "
        f"${metrics['arr']:,.2f}"
    )

    print(
        f"ARPU: "
        f"${metrics['arpu']:,.2f}"
    )

    print("\n## TIER BY CUSTOMER TYPE\n")

    tier_by_type = pd.crosstab(
        priced_customers["customer_type"],
        priced_customers["selected_tier"],
        normalize="index",
    ) * 100

    print(
        tier_by_type.round(1)
    )

    print("\n## AVERAGE CONVERSION PROBABILITY\n")

    print(
        priced_customers[
            [
                "professional_conversion_probability",
                "practice_conversion_probability",
            ]
        ]
        .mean()
        .round(3)
    )