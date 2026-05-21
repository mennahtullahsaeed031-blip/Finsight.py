FIELD_MAP = {
    "revenue": [
        "revenue", "sales", "net sales", "turnover", "total revenue",
        "income", "net revenue", "gross sales", "top line", "receipts"
    ],
    "capex": [
        "capex", "capital expenditure", "initial cost", "project cost",
        "investment", "fixed asset", "machine", "equipment", "installation",
        "asset purchase", "initial investment", "total investment"
    ],
    "operating_costs": [
        "operating costs", "opex", "operating expenses", "overhead",
        "running costs", "operational cost", "total costs", "expenses"
    ],
    "fixed_costs": [
        "fixed costs", "fixed expenses", "rent", "salaries",
        "admin", "sg&a", "general expenses", "fixed overhead"
    ],
    "variable_costs": [
        "variable costs", "variable expenses", "cogs",
        "cost of sales", "direct costs", "production cost",
        "cost of goods sold", "material cost"
    ],
    "maintenance": [
        "maintenance", "repair", "upkeep", "service cost",
        "maintenance cost", "repairs and maintenance"
    ],
    "discount_rate": [
        "discount rate", "wacc", "required return", "hurdle rate",
        "cost of capital", "minimum return", "required rate"
    ],
    "tax_rate": [
        "tax rate", "income tax", "corporate tax", "tax %",
        "taxation", "tax percentage"
    ],
    "inflation": [
        "inflation", "inflation rate", "cpi", "price increase",
        "cost inflation"
    ],
    "salvage_value": [
        "salvage value", "residual value", "terminal value",
        "scrap value", "end value"
    ],
    "working_capital": [
        "working capital", "net working capital", "nwc",
        "current assets", "liquidity"
    ]
}

SECTOR_BENCHMARKS = {
    "Expansion":          {"min_irr": 14, "max_irr": 20, "label": "General Expansion"},
    "Automation":         {"min_irr": 15, "max_irr": 22, "label": "Automation / Tech"},
    "Cost Reduction":     {"min_irr": 12, "max_irr": 18, "label": "Cost Reduction"},
    "New Product":        {"min_irr": 18, "max_irr": 28, "label": "New Product Launch"},
    "ERP Implementation": {"min_irr": 10, "max_irr": 16, "label": "ERP / IT Systems"},
    "New Branch":         {"min_irr": 12, "max_irr": 20, "label": "Branch Expansion"},
}

def map_column(col_name: str) -> str:
    col_lower = col_name.lower().strip()
    for field, aliases in FIELD_MAP.items():
        if any(alias in col_lower or col_lower in alias
               for alias in aliases):
            return field
    return "unknown"

def map_dataframe_columns(df):
    mapped = {}
    for col in df.columns:
        field = map_column(str(col))
        if field != "unknown":
            mapped[field] = col
    return mapped

def detect_statement_type(df):
    cols = ' '.join(c.lower() for c in df.columns)
    if any(k in cols for k in ["revenue", "sales", "turnover"]):
        if any(k in cols for k in ["budget", "actual", "variance"]):
            return "Budget vs Actual"
        return "Income Statement / Revenue Forecast"
    if any(k in cols for k in ["machine", "equipment", "capex", "investment"]):
        return "CapEx Proposal"
    if any(k in cols for k in ["cash", "inflow", "outflow"]):
        return "Cash Flow Forecast"
    return "General Financial Data"

def get_benchmark(project_type: str):
    return SECTOR_BENCHMARKS.get(project_type, {"min_irr": 12, "max_irr": 20, "label": "General"})

def check_assumptions(discount_rate, tax_rate, inflation,
                      revenues, fixed_costs, var_costs):
    alerts = []
    if inflation > 0.30:
        alerts.append("⚠️ Inflation rate above 30% — verify this assumption.")
    if inflation < 0.05:
        alerts.append("⚠️ Inflation below 5% may be unrealistic for Egyptian market.")
    if discount_rate < 0.08:
        alerts.append("⚠️ Discount rate below 8% seems low — verify WACC.")
    if discount_rate > 0.35:
        alerts.append("⚠️ Discount rate above 35% is very high — double-check.")
    if tax_rate > 0.40:
        alerts.append("⚠️ Tax rate above 40% — confirm with tax advisor.")
    if len(revenues) >= 2:
        for i in range(1, len(revenues)):
            if revenues[i-1] > 0:
                growth = (revenues[i] - revenues[i-1]) / revenues[i-1]
                if growth > 0.50:
                    alerts.append(f"⚠️ Revenue growth Year {i+1} is {growth*100:.0f}% — may be unrealistic.")
                if growth < -0.30:
                    alerts.append(f"⚠️ Revenue drop Year {i+1} is {abs(growth)*100:.0f}% — verify assumption.")
    total_costs = [f + v for f, v in zip(fixed_costs, var_costs)]
    for i, (rev, cost) in enumerate(zip(revenues, total_costs)):
        if rev > 0 and cost / rev > 0.95:
            alerts.append(f"⚠️ Year {i+1}: Costs are {cost/rev*100:.0f}% of revenue — very thin margin.")
    if not alerts:
        alerts.append("✅ All assumptions appear within reasonable range.")
    return alerts