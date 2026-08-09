# healthcare-saas-pricing-packaging-simulator
# Healthcare SaaS Pricing & Packaging Simulator

A healthcare SaaS pricing and packaging optimization engine that evaluates subscription prices, feature bundles, customer conversion, churn, and recurring revenue to recommend a target pricing strategy.

## Business Question

The project was built to answer:

**What should a healthcare SaaS company include in each subscription tier, and what should it charge to balance customer adoption, retention, and recurring revenue?**

The simulator models a healthcare SaaS marketplace of 10,000 synthetic customers across four segments:

- Solo Providers
- Small Practices
- Group Practices
- Large Practices

Customers have different practice sizes, feature needs, willingness to pay, and price sensitivity.

The engine then models how those customers respond to different prices and feature packages.

## How It Works

The project evaluates pricing through several layers:

**Customer Market → Conversion → Pricing → Churn → Packaging → Optimization**

The customer model estimates whether each customer selects Free, Professional, or Practice based on:

- Willingness to pay
- Price sensitivity
- Practice size
- Feature needs
- Package price
- Package feature fit

The pricing engine tests multiple Professional and Practice prices to measure the tradeoff between price and conversion.

The retention layer estimates how pricing and feature value affect expected customer churn.

The packaging engine tests different ways of bundling:

- Scheduling
- Patient Communication
- Advanced Analytics
- Claims Automation
- Practice Management

Finally, the recommendation engine evaluates **144 pricing and packaging combinations** and selects the strategy producing the highest expected retained monthly recurring revenue.

## Recommended Strategy

Under the current synthetic marketplace assumptions, the model recommends:

### Professional — $49/month

Includes:

- Scheduling
- Patient Communication

### Practice — $119/month

Includes everything in Professional plus:

- Advanced Analytics
- Claims Automation
- Practice Management

### Modeled Results

| Metric | Result |
|---|---:|
| Paid Conversion | 52.22% |
| Expected Monthly Churn | 14.93% |
| Initial MRR | $372,568 |
| Expected Retained MRR | $320,440.66 |
| Expected Retained ARR | $3,845,287.91 |
| ARPU | $37.26 |

These results are based on synthetic customer behavior and are intended to demonstrate the pricing decision framework rather than predict the economics of a real company.

## Dashboard

The Streamlit application allows users to:

- Change Professional and Practice prices
- Select different packaging strategies
- Compare Free, Professional, and Practice adoption
- Analyze paid conversion
- Evaluate expected churn
- Compare initial and retained recurring revenue
- Measure ARPU
- Review customer behavior by segment
- Run the full pricing and packaging optimizer
- View the recommended pricing strategy

## Tech Stack

- **Python** — simulation and pricing engine
- **Pandas** — customer data, segmentation, and scenario analysis
- **NumPy** — probabilistic customer behavior and reproducible simulation
- **Streamlit** — interactive pricing and packaging dashboard
- **Git/GitHub** — version control and project distribution

## Project Structure

```text
healthcare-saas-pricing-packaging-simulator/
│
├── app.py
├── README.md
├── requirements.txt
│
├── data/
│   └── processed/
│       └── synthetic_customers.csv
│
└── src/
    ├── __init__.py
    ├── generate_customers.py
    ├── pricing_model.py
    ├── scenario_engine.py
    ├── churn_model.py
    ├── packaging_engine.py
    └── recommendation_engine.py
```

## Run Locally

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/healthcare-saas-pricing-packaging-simulator.git
cd healthcare-saas-pricing-packaging-simulator
```

Create and activate a virtual environment:

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Generate the synthetic customer dataset:

```bash
python -m src.generate_customers
```

Launch the dashboard:

```bash
streamlit run app.py
```

Streamlit will provide the local address for opening the application in your browser.

## Modeling Approach

The simulator uses probabilistic customer behavior rather than automatically assigning customers to a paid tier.

Conversion probability changes based on price, willingness to pay, price sensitivity, feature fit, and customer characteristics.

Fixed random seeds are used so pricing scenarios are evaluated against the same simulated customer behavior. This reduces random variation when comparing one pricing strategy against another.

The churn model then estimates expected retention based on the relationship between subscription price, willingness to pay, price sensitivity, and feature value.

The final recommendation engine combines these layers to compare pricing and packaging strategies using expected retained revenue.

## Data Disclaimer

This project uses synthetic healthcare SaaS customer data for portfolio and demonstration purposes.

Customer behavior, pricing, conversion rates, churn, revenue, and recommended packages do not represent actual data from Headway or any other healthcare company.

## Skills Demonstrated

Healthcare SaaS pricing and packaging, subscription pricing, feature bundling, customer segmentation, probabilistic conversion modeling, churn modeling, retention analysis, MRR and ARR analysis, ARPU, scenario modeling, pricing optimization, Python, Pandas, NumPy, and Streamlit.
