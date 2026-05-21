def run_sensitivity(capex, revenues, fixed_costs,
                    var_costs, maintenance, tax_rate,
                    discount_rate):
    from calculations import calculate_npv, build_cashflows

    base_cf  = build_cashflows(capex, revenues, fixed_costs,
                                var_costs, maintenance, tax_rate)
    base_npv = calculate_npv(discount_rate, base_cf)

    results = []

    tests = [
        ("Revenue -10%",   revenues,     [r * 0.90 for r in revenues],
         fixed_costs,      var_costs,    discount_rate),
        ("Revenue -20%",   revenues,     [r * 0.80 for r in revenues],
         fixed_costs,      var_costs,    discount_rate),
        ("Revenue +10%",   revenues,     [r * 1.10 for r in revenues],
         fixed_costs,      var_costs,    discount_rate),
        ("Costs +10%",     revenues,     revenues,
         [c * 1.10 for c in fixed_costs], var_costs, discount_rate),
        ("Costs +20%",     revenues,     revenues,
         [c * 1.20 for c in fixed_costs], var_costs, discount_rate),
        ("WACC +4%",       revenues,     revenues,
         fixed_costs,      var_costs,    discount_rate + 0.04),
        ("WACC -4%",       revenues,     revenues,
         fixed_costs,      var_costs,    max(discount_rate - 0.04, 0.01)),
        ("Tax +10%",       revenues,     revenues,
         fixed_costs,      var_costs,    discount_rate),
    ]

    for label, rev_old, rev_new, fc_new, vc, dr in tests:
        tax = tax_rate + 0.10 if "Tax" in label else tax_rate
        cf  = build_cashflows(capex, rev_new, fc_new, vc, maintenance, tax)
        npv = calculate_npv(dr, cf)
        change = npv - base_npv
        pct    = (change / abs(base_npv) * 100) if base_npv != 0 else 0
        results.append({
            "Scenario":    label,
            "New NPV":     round(npv, 0),
            "Change":      round(change, 0),
            "Change %":    round(pct, 1),
            "Impact":      "🔴 High Risk" if pct < -20
                           else "🟡 Moderate" if pct < -10
                           else "🟢 Low Risk"
        })

    return results, base_npv