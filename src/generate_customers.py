import numpy as np
import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
rng = np.random.default_rng(RANDOM_SEED)


CUSTOMER_TYPES = {
    "Solo Provider": 0.50,
    "Small Practice": 0.30,
    "Group Practice": 0.15,
    "Large Practice": 0.05,
}

SPECIALTIES = [
    "Therapy",
    "Psychiatry",
    "Psychology",
    "Counseling",
]


def generate_customers(n_customers=10000):
    """
    Generate a synthetic healthcare SaaS customer market.
    """

    customer_types = rng.choice(
        list(CUSTOMER_TYPES.keys()),
        size=n_customers,
        p=list(CUSTOMER_TYPES.values()),
    )

    specialties = rng.choice(
        SPECIALTIES,
        size=n_customers,
    )

    records = []

    for customer_id, customer_type, specialty in zip(
        range(1, n_customers + 1),
        customer_types,
        specialties,
    ):

        if customer_type == "Solo Provider":
            practice_size = 1
            patient_volume = rng.integers(60, 180)
            base_wtp = 35
            sensitivity_mean = 0.80

        elif customer_type == "Small Practice":
            practice_size = rng.integers(2, 6)
            patient_volume = rng.integers(150, 600)
            base_wtp = 65
            sensitivity_mean = 0.65

        elif customer_type == "Group Practice":
            practice_size = rng.integers(6, 16)
            patient_volume = rng.integers(500, 1800)
            base_wtp = 120
            sensitivity_mean = 0.45

        else:
            practice_size = rng.integers(16, 41)
            patient_volume = rng.integers(1500, 5000)
            base_wtp = 190
            sensitivity_mean = 0.30

        scheduling_need = np.clip(
            rng.normal(0.70, 0.15),
            0,
            1,
        )

        communication_need = np.clip(
            rng.normal(0.65, 0.18),
            0,
            1,
        )

        analytics_need = np.clip(
            rng.normal(
                0.45 + practice_size * 0.015,
                0.15,
            ),
            0,
            1,
        )

        claims_need = np.clip(
            rng.normal(
                0.50 + practice_size * 0.012,
                0.17,
            ),
            0,
            1,
        )

        management_need = np.clip(
            rng.normal(
                0.35 + practice_size * 0.018,
                0.15,
            ),
            0,
            1,
        )

        price_sensitivity = np.clip(
            rng.normal(
                sensitivity_mean,
                0.10,
            ),
            0.05,
            1.00,
        )

        feature_value_score = (
            scheduling_need * 8
            + communication_need * 7
            + analytics_need * 12
            + claims_need * 15
            + management_need * 18
        )

        willingness_to_pay = (
            base_wtp
            + feature_value_score
            + practice_size * 2
            + rng.normal(0, 12)
        )

        willingness_to_pay = max(
            willingness_to_pay,
            10,
        )

        records.append(
            {
                "customer_id": f"C{customer_id:05d}",
                "customer_type": customer_type,
                "specialty": specialty,
                "practice_size": int(practice_size),
                "monthly_patient_volume": int(patient_volume),
                "scheduling_need": round(scheduling_need, 3),
                "patient_communication_need": round(
                    communication_need,
                    3,
                ),
                "analytics_need": round(
                    analytics_need,
                    3,
                ),
                "claims_automation_need": round(
                    claims_need,
                    3,
                ),
                "practice_management_need": round(
                    management_need,
                    3,
                ),
                "willingness_to_pay": round(
                    willingness_to_pay,
                    2,
                ),
                "price_sensitivity": round(
                    price_sensitivity,
                    3,
                ),
            }
        )

    return pd.DataFrame(records)


def save_customers(df):
    output_path = (
        PROCESSED_DATA_DIR
        / "synthetic_customers.csv"
    )

    df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Generated {len(df):,} healthcare SaaS customers"
    )

    print(
        f"Saved dataset to: {output_path}"
    )

    return output_path


if __name__ == "__main__":

    customers = generate_customers()

    save_customers(customers)

    print("\nCustomer preview:")
    print(customers.head())

    print("\nCustomer segment summary:")

    print(
        customers.groupby(
            "customer_type"
        )[
            [
                "practice_size",
                "monthly_patient_volume",
                "willingness_to_pay",
                "price_sensitivity",
            ]
        ]
        .mean()
        .round(2)
    )