import numpy as np

def calculate_npv(discount_rate, cashflows):
    npv = 0
    for i, cf in enumerate(cashflows):
        npv += cf / (1 + discount_rate) ** i
    return npv

def calculate_irr(cashflows):
    rate = 0.1
    for _ in range(2000):
        npv = sum(cf / (1 + rate) ** i
                  for i, cf in enumerate(cashflows))
        d_npv = sum(-i * cf / (1 + rate) ** (i + 1)
                    for i, cf in enumerate(cashflows))
        if abs(d_npv) < 1e-10:
            break
        rate -= npv / d_npv
        if rate <= -1:
            return None
    return rate * 100

def calculate_payback(cashflows):
    cumulative = 0
    for i, cf in enumerate(cashflows):
        cumulative += cf
        if cumulative >= 0:
            return i
    return None

def calculate_profitability_index(npv, initial_investment):
    if initial_investment == 0:
        return None
    return 1 + (npv / abs(initial_investment))

def calculate_future_value(initial, monthly, rate, years):
    months = years * 12
    monthly_rate = rate / 12
    fv_initial = initial * (1 + monthly_rate) ** months
    if monthly_rate > 0:
        fv_monthly = monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        fv_monthly = monthly * months
    return fv_initial + fv_monthly

def build_cashflows(capex, revenues, fixed_costs,
                    variable_costs, maintenance, tax_rate):
    cashflows = [-abs(capex)]
    for i in range(len(revenues)):
        rev  = revenues[i]
        cost = fixed_costs[i] + variable_costs[i] + maintenance[i]
        ebt  = rev - cost
        tax  = ebt * tax_rate if ebt > 0 else 0
        net  = ebt - tax
        cashflows.append(net)
    return cashflows

def run_scenarios(capex, revenues, fixed_costs,
                  variable_costs, maintenance, tax_rate, discount_rate):
    base_cf = build_cashflows(capex, revenues, fixed_costs,
                               variable_costs, maintenance, tax_rate)

    best_rev  = [r * 1.10 for r in revenues]
    best_fc   = [c * 0.95 for c in fixed_costs]
    best_cf   = build_cashflows(capex, best_rev, best_fc,
                                variable_costs, maintenance, tax_rate)

    worst_rev = [r * 0.90 for r in revenues]
    worst_fc  = [c * 1.10 for c in fixed_costs]
    worst_cf  = build_cashflows(capex, worst_rev, worst_fc,
                                variable_costs, maintenance, tax_rate)

    def metrics(cf):
        npv     = calculate_npv(discount_rate, cf)
        irr     = calculate_irr(cf)
        payback = calculate_payback(cf)
        pi      = calculate_profitability_index(npv, capex)
        return {
            'npv':       npv,
            'irr':       irr,
            'payback':   payback,
            'pi':        pi,
            'cashflows': cf
        }

    return {
        'base':  metrics(base_cf),
        'best':  metrics(best_cf),
        'worst': metrics(worst_cf)
    }