import numpy as np
import pandas as pd


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def estimate_churn_probability(df):
    """
    Estimate monthly churn probability for paying customers.
    """

    result = df.copy()

    result["churn_probability"] = 0.0

    professional_mask = (
        result["selected_tier"] == "Professional"
    )

    practice_mask = (
        result["selected_tier"] == "Practice"
    )

    professional_price_pressure = (
        result["monthly_price"]
        / result["willingness_to_pay"]
    )

    practice_price_pressure = (
        result["monthly_price"]
        / result["willingness_to_pay"]
    )

    professional_churn_score = (
        -3.0
        + 2.5 * professional_price_pressure
        + 1.5 * result["price_sensitivity"]
        - 1.5 * result["professional_feature_fit"]
    )

    practice_churn_score = (
        -3.2
        + 2.3 * practice_price_pressure
        + 1.3 * result["price_sensitivity"]
        - 1.7 * result["practice_feature_fit"]
    )

    result.loc[
        professional_mask,
        "churn_probability",
    ] = sigmoid(
        professional_churn_score[
            professional_mask
        ]
    )

    result.loc[
        practice_mask,
        "churn_probability",
    ] = sigmoid(
        practice_churn_score[
            practice_mask
        ]
    )

    return result


def calculate_retention_metrics(df):
    """
    Calculate expected retained customers and retained revenue
    after applying modeled monthly churn.
    """

    result = df.copy()

    result["retention_probability"] = (
        1 - result["churn_probability"]
    )

    result["expected_retained_revenue"] = (
        result["monthly_price"]
        * result["retention_probability"]
    )

    paying_customers = result[
        result["selected_tier"] != "Free"
    ]

    avg_churn = (
        paying_customers["churn_probability"].mean()
    )

    retained_mrr = (
        result["expected_retained_revenue"].sum()
    )

    retained_arr = retained_mrr * 12

    return {
        "average_monthly_churn": avg_churn,
        "retained_mrr": retained_mrr,
        "retained_arr": retained_arr,
    }


if __name__ == "__main__":

    from pathlib import Path
    from src.pricing_model import (
        assign_tiers,
        calculate_saas_metrics,
    )

    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    DATA_PATH = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "synthetic_customers.csv"
    )

    customers = pd.read_csv(
        DATA_PATH
    )

    priced_customers = assign_tiers(
        customers,
        professional_price=49,
        practice_price=149,
    )

    priced_customers = estimate_churn_probability(
        priced_customers
    )

    pricing_metrics = calculate_saas_metrics(
        priced_customers
    )

    retention_metrics = calculate_retention_metrics(
        priced_customers
    )

    print("\n## RETENTION / CHURN RESULTS\n")

    print(
        f"Paid conversion rate: "
        f"{pricing_metrics['paid_conversion_rate']:.2%}"
    )

    print(
        f"Initial MRR: "
        f"${pricing_metrics['mrr']:,.2f}"
    )

    print(
        f"Average monthly churn: "
        f"{retention_metrics['average_monthly_churn']:.2%}"
    )

    print(
        f"Expected retained MRR: "
        f"${retention_metrics['retained_mrr']:,.2f}"
    )

    print(
        f"Expected retained ARR: "
        f"${retention_metrics['retained_arr']:,.2f}"
    )

    print("\nChurn by tier:")

    print(
        priced_customers[
            priced_customers["selected_tier"] != "Free"
        ]
        .groupby("selected_tier")[
            "churn_probability"
        ]
        .mean()
        .round(3)
    )