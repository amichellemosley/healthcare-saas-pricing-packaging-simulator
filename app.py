import pandas as pd
import streamlit as st
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

from src.recommendation_engine import (
    run_full_pricing_packaging_analysis,
    find_best_strategy,
)


st.set_page_config(
    page_title="Healthcare SaaS Pricing & Packaging Simulator",
    page_icon="💳",
    layout="wide",
)


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "synthetic_customers.csv"


@st.cache_data
def load_customers():
    return pd.read_csv(DATA_PATH)


customers = load_customers()


st.title("Healthcare SaaS Pricing & Packaging Simulator")

st.caption(
    "Test healthcare SaaS prices, feature bundles, conversion, churn, "
    "ARPU, and retained revenue to evaluate pricing and packaging strategy."
)


# ---------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------

st.sidebar.header("Pricing Strategy")

strategy_name = st.sidebar.selectbox(
    "Packaging strategy",
    list(PACKAGE_STRATEGIES.keys()),
)

professional_price = st.sidebar.slider(
    "Professional price ($/month)",
    min_value=19,
    max_value=99,
    value=49,
    step=5,
)

practice_price = st.sidebar.slider(
    "Practice price ($/month)",
    min_value=79,
    max_value=219,
    value=119,
    step=10,
)

run_scenario = st.sidebar.button(
    "Evaluate Strategy",
    type="primary",
)


# ---------------------------------------------------------
# Selected package
# ---------------------------------------------------------

strategy = PACKAGE_STRATEGIES[strategy_name]

st.subheader("Selected Package Design")

package_col1, package_col2 = st.columns(2)

with package_col1:
    st.markdown("### Professional")
    st.write(f"**${professional_price}/month**")

    for feature in strategy["professional_features"]:
        st.write(f"✓ {feature.title()}")

with package_col2:
    st.markdown("### Practice")
    st.write(f"**${practice_price}/month**")

    for feature in strategy["professional_features"]:
        st.write(f"✓ {feature.title()}")

    for feature in strategy["practice_features"]:
        st.write(f"✓ {feature.title()}")


# ---------------------------------------------------------
# Evaluate selected strategy
# ---------------------------------------------------------

if run_scenario:

    priced = assign_tiers_with_packaging(
        customers,
        professional_features=strategy["professional_features"],
        practice_features=strategy["practice_features"],
        professional_price=professional_price,
        practice_price=practice_price,
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

    # -----------------------------------------------------
    # KPI summary
    # -----------------------------------------------------

    st.divider()

    st.header("Pricing Performance")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Paid Conversion",
        f"{pricing_metrics['paid_conversion_rate']:.2%}",
    )

    col2.metric(
        "Expected Monthly Churn",
        f"{retention_metrics['average_monthly_churn']:.2%}",
    )

    col3.metric(
        "Retained MRR",
        f"${retention_metrics['retained_mrr']:,.0f}",
    )

    col4.metric(
        "ARPU",
        f"${pricing_metrics['arpu']:,.2f}",
    )

    col5, col6, col7 = st.columns(3)

    col5.metric(
        "Initial MRR",
        f"${pricing_metrics['mrr']:,.0f}",
    )

    col6.metric(
        "Retained ARR",
        f"${retention_metrics['retained_arr']:,.0f}",
    )

    col7.metric(
        "Paid Customers",
        f"{pricing_metrics['paid_customers']:,}",
    )

    # -----------------------------------------------------
    # Tier mix
    # -----------------------------------------------------

    st.subheader("Customer Tier Mix")

    tier_df = pd.DataFrame(
        {
            "Tier": [
                "Free",
                "Professional",
                "Practice",
            ],
            "Customers": [
                tier_counts.get("Free", 0),
                tier_counts.get("Professional", 0),
                tier_counts.get("Practice", 0),
            ],
        }
    )

    st.bar_chart(
        tier_df.set_index("Tier"),
    )

    st.dataframe(
        tier_df,
        use_container_width=True,
        hide_index=True,
    )

    # -----------------------------------------------------
    # Segment behavior
    # -----------------------------------------------------

    st.subheader("Tier Selection by Customer Segment")

    segment_mix = pd.crosstab(
        priced["customer_type"],
        priced["selected_tier"],
        normalize="index",
    ) * 100

    st.dataframe(
        segment_mix.round(1),
        use_container_width=True,
    )

    # -----------------------------------------------------
    # Revenue + retention
    # -----------------------------------------------------

    st.subheader("Revenue and Retention")

    revenue_df = pd.DataFrame(
        {
            "Metric": [
                "Initial MRR",
                "Expected Retained MRR",
            ],
            "Value": [
                pricing_metrics["mrr"],
                retention_metrics["retained_mrr"],
            ],
        }
    )

    st.bar_chart(
        revenue_df.set_index("Metric"),
    )

    # -----------------------------------------------------
    # Full optimization
    # -----------------------------------------------------

    st.divider()

    st.header("Pricing + Packaging Optimization")

    st.write(
        "The optimizer evaluates all packaging strategies across "
        "multiple Professional and Practice price points and selects "
        "the configuration with the highest expected retained MRR."
    )

    with st.spinner(
        "Evaluating pricing and packaging combinations..."
    ):

        optimization_results = (
            run_full_pricing_packaging_analysis(
                customers
            )
        )

        best = find_best_strategy(
            optimization_results
        )

    st.subheader("Recommended Strategy")

    rec1, rec2, rec3, rec4 = st.columns(4)

    rec1.metric(
        "Professional Price",
        f"${best['professional_price']:.0f}",
    )

    rec2.metric(
        "Practice Price",
        f"${best['practice_price']:.0f}",
    )

    rec3.metric(
        "Paid Conversion",
        f"{best['paid_conversion_rate']:.2%}",
    )

    rec4.metric(
        "Retained MRR",
        f"${best['retained_mrr']:,.0f}",
    )

    st.success(
        f"Recommended Package: {best['strategy']}"
    )

    st.write(
        f"**Professional includes:** "
        f"{best['professional_features']}"
    )

    st.write(
        f"**Practice additionally includes:** "
        f"{best['practice_only_features']}"
    )

    result_col1, result_col2, result_col3 = st.columns(3)

    result_col1.metric(
        "Expected Monthly Churn",
        f"{best['monthly_churn']:.2%}",
    )

    result_col2.metric(
        "Retained ARR",
        f"${best['retained_arr']:,.0f}",
    )

    result_col3.metric(
        "ARPU",
        f"${best['arpu']:,.2f}",
    )

    # -----------------------------------------------------
    # Top strategies
    # -----------------------------------------------------

    st.subheader("Top Pricing + Packaging Scenarios")

    top_scenarios = (
        optimization_results
        .sort_values(
            "retained_mrr",
            ascending=False,
        )
        .head(10)
        .copy()
    )

    top_scenarios = top_scenarios[
        [
            "strategy",
            "professional_price",
            "practice_price",
            "paid_conversion_rate",
            "monthly_churn",
            "retained_mrr",
            "arpu",
        ]
    ]

    top_scenarios.columns = [
        "Package Strategy",
        "Professional Price",
        "Practice Price",
        "Paid Conversion",
        "Monthly Churn",
        "Retained MRR",
        "ARPU",
    ]

    st.dataframe(
        top_scenarios.style.format(
            {
                "Professional Price": "${:,.0f}",
                "Practice Price": "${:,.0f}",
                "Paid Conversion": "{:.2%}",
                "Monthly Churn": "{:.2%}",
                "Retained MRR": "${:,.0f}",
                "ARPU": "${:,.2f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


else:

    st.info(
        "Choose a package strategy and prices in the sidebar, "
        "then click **Evaluate Strategy**."
    )