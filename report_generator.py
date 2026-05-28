from fpdf import FPDF
from datetime import datetime

class CFOReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 13)
        self.cell(0, 10, 'FinSight - Corporate Investment Report', ln=True, align='C')
        self.set_font('Arial', '', 9)
        self.cell(0, 6, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} - Confidential', align='C')

def generate_report(project_name, project_type, scenarios, ai_memo, path='investment_report.pdf'):
    pdf = CFOReport()
    pdf.add_page()

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, f'Project: {project_name}', ln=True)
    pdf.cell(0, 8, f'Type: {project_type}', ln=True)
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'Financial Summary', ln=True)
    pdf.ln(2)

    headers = ['Metric', 'Worst Case', 'Base Case', 'Best Case']
    widths  = [55, 42, 42, 42]

    pdf.set_font('Arial', 'B', 9)
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=1, align='C')
    pdf.ln()

    pdf.set_font('Arial', '', 9)
    s = scenarios

    def fmt_irr(v):
        return f"{v:.1f}%" if v is not None else "N/A"

    def fmt_pb(v):
        return f"Year {v}" if v is not None else "Not recovered"

    def fmt_pi(v):
        return f"{v:.2f}" if v is not None else "N/A"

    rows = [
        ['NPV',
         f"{s['worst']['npv']:,.0f}",
         f"{s['base']['npv']:,.0f}",
         f"{s['best']['npv']:,.0f}"],
        ['IRR',
         fmt_irr(s['worst']['irr']),
         fmt_irr(s['base']['irr']),
         fmt_irr(s['best']['irr'])],
        ['Payback',
         fmt_pb(s['worst']['payback']),
         fmt_pb(s['base']['payback']),
         fmt_pb(s['best']['payback'])],
        ['Prof. Index',
         fmt_pi(s['worst']['pi']),
         fmt_pi(s['base']['pi']),
         fmt_pi(s['best']['pi'])],
    ]

    for row in rows:
        for val, w in zip(row, widths):
            pdf.cell(w, 6, str(val), border=1, align='C')
        pdf.ln()

    pdf.ln(6)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'AI CFO Recommendation', ln=True)
    pdf.set_font('Arial', '', 9)

    clean_memo = ai_memo.encode('latin-1', errors='replace').decode('latin-1')
    for line in clean_memo.split('\n'):
        pdf.multi_cell(0, 5, line)

    pdf.output(path)
    return path
