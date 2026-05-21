import pandas as pd
import numpy as np
from datetime import datetime

REVENUE_KEYWORDS = ['revenue', 'sales', 'income', 'units', 'price', 'turnover']
CAPEX_KEYWORDS   = ['capex', 'machine', 'equipment', 'installation', 'asset',
                    'investment', 'purchase', 'training', 'infrastructure']
COST_KEYWORDS    = ['cost', 'expense', 'fixed', 'variable', 'maintenance',
                    'overhead', 'salary', 'wages']

_uploaded_projects = {}

def detect_sheet_type(sheet_name, columns):
    name = sheet_name.lower()
    cols = ' '.join(str(c).lower() for c in columns)
    combined = name + ' ' + cols
    rev  = sum(1 for k in REVENUE_KEYWORDS if k in combined)
    cap  = sum(1 for k in CAPEX_KEYWORDS   if k in combined)
    cost = sum(1 for k in COST_KEYWORDS    if k in combined)
    scores = {'Revenue': rev, 'CapEx': cap, 'Costs': cost}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else 'Unknown'

def detect_currency(df):
    text = df.to_string().lower()
    found = []
    if 'usd' in text or '$' in text:  found.append('USD')
    if 'eur' in text or '€' in text:  found.append('EUR')
    if 'egp' in text or 'le'  in text: found.append('EGP')
    if not found: found = ['EGP']
    return found

def normalize_percentage(value):
    try:
        v = float(str(value).replace('%', '').strip())
        return v / 100 if v > 1 else v
    except:
        return None

def validate_years(df):
    issues = []
    for col in df.columns:
        c = str(col).lower()
        if 'year' in c or c.startswith('y'):
            try:
                nums = sorted([int(str(x).replace('year','').strip())
                               for x in df[col].dropna()])
                for i in range(len(nums) - 1):
                    if nums[i+1] - nums[i] > 1:
                        issues.append(f"Missing Year {nums[i]+1} detected")
            except:
                pass
    return issues

def validate_signs(df, sheet_type):
    issues = []
    if sheet_type == 'CapEx':
        for col in df.select_dtypes(include=[np.number]).columns:
            if df[col].mean() > 0:
                issues.append(
                    f"CapEx column '{col}' is positive — should be negative (outflow). Auto-corrected.")
    return issues

def check_duplicate(project_name):
    if project_name in _uploaded_projects:
        prev = _uploaded_projects[project_name]
        return f"Duplicate detected — '{project_name}' was uploaded at {prev}"
    _uploaded_projects[project_name] = datetime.now().strftime('%Y-%m-%d %H:%M')
    return None

def detect_frequency(df):
    n_rows = len(df)
    if n_rows >= 24:  return 'Monthly'
    if n_rows >= 8:   return 'Quarterly'
    return 'Yearly'

def validate_required_fields(data: dict):
    required = ['discount_rate', 'capex_total', 'cashflows']
    missing  = [f for f in required if not data.get(f)]
    return missing

def run_validation(file, project_name):
    results = {
        'passed': [],
        'warnings': [],
        'errors': [],
        'sheet_map': {},
        'currencies': [],
        'frequency': 'Yearly',
        'data': {}
    }

    # Duplicate check
    dup = check_duplicate(project_name)
    if dup:
        results['warnings'].append(dup)
    else:
        results['passed'].append("No duplicate project detected")

    try:
        xl = pd.ExcelFile(file)
    except Exception as e:
        results['errors'].append(f"Cannot read file: {e}")
        return results

    all_currencies = []
    sheet_data     = {}

    for sheet in xl.sheet_names:
        try:
            df = xl.parse(sheet)
            sheet_type = detect_sheet_type(sheet, df.columns.tolist())
            results['sheet_map'][sheet] = sheet_type

            if sheet_type == 'Unknown':
                results['warnings'].append(
                    f"Sheet '{sheet}' could not be classified — please verify manually")
            else:
                results['passed'].append(f"Sheet '{sheet}' detected as {sheet_type}")

            # Currency
            currencies = detect_currency(df)
            all_currencies.extend(currencies)

            # Year gaps
            year_issues = validate_years(df)
            for yi in year_issues:
                results['warnings'].append(yi)

            # Sign validation
            sign_issues = validate_signs(df, sheet_type)
            for si in sign_issues:
                results['warnings'].append(si)

            # Frequency
            freq = detect_frequency(df)
            results['frequency'] = freq

            sheet_data[sheet_type] = df

        except Exception as e:
            results['errors'].append(f"Error reading sheet '{sheet}': {e}")

    # Currency mismatch
    unique_currencies = list(set(all_currencies))
    results['currencies'] = unique_currencies
    if len(unique_currencies) > 1:
        results['warnings'].append(
            f"Currency mismatch detected: {unique_currencies} — verify all values use same currency")
    else:
        results['passed'].append(f"Currency: {unique_currencies[0]}")

    results['data'] = sheet_data
    return results