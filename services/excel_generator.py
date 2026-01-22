from pathlib import Path
from typing import List, Dict
import pandas as pd
from openpyxl import load_workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from services.categorizer import get_category_summary, get_monthly_summary
from datetime import datetime


def generate_cfo_pack(transactions: List[Dict], output_path: Path):
    """
    Generate Professional CFO Pack with:
    1. Dashboard (Summary + Charts)
    2. All Transactions
    3. Monthly Analysis
    4. Category Analysis
    5. How to Use
    """

    # Calculate key metrics
    total_income = sum(t["amount"] for t in transactions if t["amount"] > 0)
    total_expenses = abs(sum(t["amount"] for t in transactions if t["amount"] < 0))
    net_income = total_income - total_expenses

    # Get date range
    dates = [datetime.strptime(t["date"], "%Y-%m-%d") for t in transactions]
    start_date = min(dates)
    end_date = max(dates)
    months_count = len(set(d.strftime("%Y-%m") for d in dates))

    # Get summaries
    monthly_summary = get_monthly_summary(transactions)
    category_summary = get_category_summary(transactions)

    # Create Excel writer
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

        # Sheet 1: Dashboard Overview
        create_dashboard_sheet(
            writer,
            transactions,
            total_income,
            total_expenses,
            net_income,
            start_date,
            end_date,
            months_count,
        )

        # Sheet 2: All Transactions
        df_transactions = pd.DataFrame(transactions)
        df_transactions = df_transactions[
            ["date", "description", "category", "amount", "type"]
        ]
        df_transactions = df_transactions.sort_values(
            "date", ascending=False
        )  # Most recent first
        df_transactions.to_excel(writer, sheet_name="All Transactions", index=False)

        # Sheet 3: Monthly Analysis
        df_monthly = pd.DataFrame.from_dict(monthly_summary, orient="index")
        df_monthly.index.name = "Month"
        df_monthly = df_monthly.reset_index()
        df_monthly = df_monthly.sort_values("Month")
        df_monthly.to_excel(writer, sheet_name="Monthly Analysis", index=False)

        # Sheet 4: Category Analysis
        df_categories = pd.DataFrame(
            [
                {
                    "Category": cat,
                    "Amount": amt,
                    "Percentage": (abs(amt) / total_expenses * 100) if amt < 0 else 0,
                }
                for cat, amt in sorted(
                    category_summary.items(), key=lambda x: abs(x[1]), reverse=True
                )
            ]
        )
        df_categories.to_excel(writer, sheet_name="Category Analysis", index=False)

        # Sheet 5: How to Use
        create_instructions_sheet(writer)

    # Load workbook to add formatting and charts
    workbook = load_workbook(output_path)

    # Format each sheet
    format_dashboard_sheet(workbook["Dashboard"], monthly_summary, category_summary)
    format_transactions_sheet(workbook["All Transactions"])
    format_monthly_sheet(workbook["Monthly Analysis"])
    format_category_sheet(workbook["Category Analysis"])
    format_instructions_sheet(workbook["How to Use"])

    # Save final workbook
    workbook.save(output_path)


def create_dashboard_sheet(
    writer,
    transactions,
    total_income,
    total_expenses,
    net_income,
    start_date,
    end_date,
    months_count,
):
    """Create dashboard with summary metrics"""

    # Create summary data
    summary_data = {
        "Metric": [
            "Total Income",
            "Total Expenses",
            "Net Income",
            "Statement Period",
            "Months Analyzed",
            "Total Transactions",
        ],
        "Value": [
            f"${total_income:,.2f}",
            f"${total_expenses:,.2f}",
            f"${net_income:,.2f}",
            f'{start_date.strftime("%b %d, %Y")} - {end_date.strftime("%b %d, %Y")}',
            str(months_count),
            str(len(transactions)),
        ],
    }

    df_summary = pd.DataFrame(summary_data)
    df_summary.to_excel(writer, sheet_name="Dashboard", index=False, startrow=1)


def create_instructions_sheet(writer):
    """Create instructions page"""

    instructions = [
        ["BankToCFO - How to Use Your CFO Pack", ""],
        ["", ""],
        [
            "What is this?",
            "Your bank statement has been converted into a professional financial report with AI-powered categorization.",
        ],
        ["", ""],
        ["Sheets Overview:", ""],
        ["", ""],
        [
            "1. Dashboard",
            "Quick overview of your finances with key metrics and visualizations",
        ],
        [
            "2. All Transactions",
            "Complete list of all transactions, sorted by date with categories",
        ],
        [
            "3. Monthly Analysis",
            "Month-by-month breakdown of income, expenses, and net income",
        ],
        ["4. Category Analysis", "Spending breakdown by category with percentages"],
        ["5. How to Use", "This page - instructions and tips"],
        ["", ""],
        ["Understanding Categories:", ""],
        ["• Revenue/Income", "Money coming in (salary, payments received, etc)"],
        ["• Fast Food", "Quick service restaurants (Chipotle, McDonald's, etc)"],
        ["• Restaurants", "Sit-down dining, bars, cafes"],
        ["• Gas & Fuel", "Gas stations, fuel purchases"],
        ["• Subscriptions", "Recurring services (Netflix, Spotify, etc)"],
        ["• Groceries", "Supermarkets, grocery stores"],
        ["• Shopping", "Retail purchases (Amazon, Target, etc)"],
        ["• Debt Payments", "Loan payments, credit card payments"],
        ["• Fitness", "Gym memberships, fitness classes"],
        ["• Healthcare", "Medical, dental, pharmacy"],
        ["• Transportation", "Uber, Lyft, parking, tolls"],
        ["• Utilities", "Electric, internet, phone bills"],
        ["• Insurance", "All insurance payments"],
        ["", ""],
        ["Tips for Better Insights:", ""],
        ["1.", "Compare monthly spending to identify trends"],
        ["2.", "Look for unexpected high-spend categories"],
        ["3.", 'Review "Other Expense" category for miscategorized items'],
        ["4.", "Use this for tax preparation and expense tracking"],
        ["5.", "Upload multiple months to see spending patterns over time"],
        ["", ""],
        ["Need Help?", "Contact support@banktocfo.com"],
        ["", ""],
        [
            "Note:",
            "AI categorization is 85-90% accurate. Review categories for tax purposes.",
        ],
    ]

    df_instructions = pd.DataFrame(instructions, columns=["Section", "Details"])
    df_instructions.to_excel(writer, sheet_name="How to Use", index=False)


def format_dashboard_sheet(sheet, monthly_summary, category_summary):
    """Format the Dashboard sheet with professional styling"""

    # Title
    sheet["A1"] = "Financial Dashboard"
    sheet["A1"].font = Font(size=20, bold=True, color="168C54")
    sheet.merge_cells("A1:B1")

    # Format summary metrics section
    header_fill = PatternFill(
        start_color="168C54", end_color="168C54", fill_type="solid"
    )
    header_font = Font(bold=True, color="FFFFFF", size=12)

    # Headers
    sheet["A2"].fill = header_fill
    sheet["A2"].font = header_font
    sheet["B2"].fill = header_fill
    sheet["B2"].font = header_font

    # Column widths
    sheet.column_dimensions["A"].width = 25
    sheet.column_dimensions["B"].width = 40

    # Format metric rows
    for row in range(3, 9):
        sheet[f"A{row}"].font = Font(bold=True, size=11)
        sheet[f"B{row}"].font = Font(size=11)

        # Add light gray background to alternating rows
        if row % 2 == 0:
            sheet[f"A{row}"].fill = PatternFill(
                start_color="F8F9FA", end_color="F8F9FA", fill_type="solid"
            )
            sheet[f"B{row}"].fill = PatternFill(
                start_color="F8F9FA", end_color="F8F9FA", fill_type="solid"
            )

    # Highlight Net Income in green or red
    net_income_value = sheet["B5"].value
    if net_income_value and "-" in str(net_income_value):
        sheet["B5"].font = Font(bold=True, color="DC3545", size=12)  # Red for negative
    else:
        sheet["B5"].font = Font(
            bold=True, color="28A745", size=12
        )  # Green for positive

    # Add Monthly Cashflow Chart
    add_monthly_chart(sheet, monthly_summary, start_row=11)

    # Add Category Breakdown Chart
    add_category_chart(sheet, category_summary, start_row=28)


def add_monthly_chart(sheet, monthly_summary, start_row):
    """Add monthly cashflow bar chart to dashboard"""

    # Add section title
    sheet[f"A{start_row}"] = "Monthly Cashflow"
    sheet[f"A{start_row}"].font = Font(size=14, bold=True, color="168C54")

    # Add data for chart
    start_row += 2
    sheet[f"A{start_row}"] = "Month"
    sheet[f"B{start_row}"] = "Income"
    sheet[f"C{start_row}"] = "Expenses"

    # Header formatting
    for col in ["A", "B", "C"]:
        cell = sheet[f"{col}{start_row}"]
        cell.fill = PatternFill(
            start_color="168C54", end_color="168C54", fill_type="solid"
        )
        cell.font = Font(bold=True, color="FFFFFF")

    # Add monthly data
    row = start_row + 1
    for month, data in sorted(monthly_summary.items()):
        sheet[f"A{row}"] = month
        sheet[f"B{row}"] = data["revenue"]
        sheet[f"C{row}"] = data["expenses"]

        # Format currency
        sheet[f"B{row}"].number_format = "$#,##0.00"
        sheet[f"C{row}"].number_format = "$#,##0.00"

        row += 1

    # Create bar chart
    chart = BarChart()
    chart.type = "col"
    chart.style = 10
    chart.title = "Monthly Income vs Expenses"
    chart.y_axis.title = "Amount ($)"
    chart.x_axis.title = "Month"
    chart.height = 10
    chart.width = 16

    # Add data
    data = Reference(sheet, min_col=2, min_row=start_row, max_row=row - 1, max_col=3)
    cats = Reference(sheet, min_col=1, min_row=start_row + 1, max_row=row - 1)

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)

    # Position chart
    sheet.add_chart(chart, f"E{start_row}")


def add_category_chart(sheet, category_summary, start_row):
    """Add category breakdown chart to dashboard"""

    # Add section title
    sheet[f"A{start_row}"] = "Top Spending Categories"
    sheet[f"A{start_row}"].font = Font(size=14, bold=True, color="168C54")

    # Add data for chart (top 10 expenses only)
    start_row += 2
    sheet[f"A{start_row}"] = "Category"
    sheet[f"B{start_row}"] = "Amount"

    # Header formatting
    for col in ["A", "B"]:
        cell = sheet[f"{col}{start_row}"]
        cell.fill = PatternFill(
            start_color="168C54", end_color="168C54", fill_type="solid"
        )
        cell.font = Font(bold=True, color="FFFFFF")

    # Add category data (expenses only, sorted by amount)
    expenses = {k: abs(v) for k, v in category_summary.items() if v < 0}
    top_expenses = sorted(expenses.items(), key=lambda x: x[1], reverse=True)[:10]

    row = start_row + 1
    for category, amount in top_expenses:
        sheet[f"A{row}"] = category
        sheet[f"B{row}"] = amount
        sheet[f"B{row}"].number_format = "$#,##0.00"
        row += 1

    # Create horizontal bar chart
    chart = BarChart()
    chart.type = "bar"  # Horizontal bars
    chart.style = 11
    chart.title = "Spending by Category"
    chart.x_axis.title = "Amount ($)"
    chart.height = 12
    chart.width = 16

    # Add data
    data = Reference(sheet, min_col=2, min_row=start_row, max_row=row - 1)
    cats = Reference(sheet, min_col=1, min_row=start_row + 1, max_row=row - 1)

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)

    # Position chart
    sheet.add_chart(chart, f"E{start_row}")


def format_transactions_sheet(sheet):
    """Format the All Transactions sheet"""

    # Header formatting
    header_fill = PatternFill(
        start_color="168C54", end_color="168C54", fill_type="solid"
    )
    header_font = Font(bold=True, color="FFFFFF", size=12)

    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Column widths
    sheet.column_dimensions["A"].width = 12  # Date
    sheet.column_dimensions["B"].width = 55  # Description
    sheet.column_dimensions["C"].width = 22  # Category
    sheet.column_dimensions["D"].width = 15  # Amount
    sheet.column_dimensions["E"].width = 10  # Type

    # Format amounts as currency with color coding
    for row in range(2, sheet.max_row + 1):
        amount_cell = sheet[f"D{row}"]
        amount_cell.number_format = "$#,##0.00"
        amount_cell.alignment = Alignment(horizontal="right")

        # Color code: red for expenses, green for income
        if amount_cell.value and amount_cell.value < 0:
            amount_cell.font = Font(color="DC3545", bold=True)
        else:
            amount_cell.font = Font(color="28A745", bold=True)

        # Alternate row colors
        if row % 2 == 0:
            for col in ["A", "B", "C", "D", "E"]:
                sheet[f"{col}{row}"].fill = PatternFill(
                    start_color="F8F9FA", end_color="F8F9FA", fill_type="solid"
                )

    # Freeze top row
    sheet.freeze_panes = "A2"


def format_monthly_sheet(sheet):
    """Format Monthly Analysis sheet"""

    # Header formatting
    header_fill = PatternFill(
        start_color="168C54", end_color="168C54", fill_type="solid"
    )
    header_font = Font(bold=True, color="FFFFFF", size=12)

    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Column widths
    sheet.column_dimensions["A"].width = 12
    sheet.column_dimensions["B"].width = 18
    sheet.column_dimensions["C"].width = 18
    sheet.column_dimensions["D"].width = 18

    # Format currency
    for row in range(2, sheet.max_row + 1):
        for col in ["B", "C", "D"]:
            cell = sheet[f"{col}{row}"]
            cell.number_format = "$#,##0.00"
            cell.alignment = Alignment(horizontal="right")

        # Color code net income
        net_cell = sheet[f"D{row}"]
        if net_cell.value and net_cell.value < 0:
            net_cell.font = Font(color="DC3545", bold=True)
        else:
            net_cell.font = Font(color="28A745", bold=True)


def format_category_sheet(sheet):
    """Format Category Analysis sheet"""

    # Header formatting
    header_fill = PatternFill(
        start_color="168C54", end_color="168C54", fill_type="solid"
    )
    header_font = Font(bold=True, color="FFFFFF", size=12)

    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Column widths
    sheet.column_dimensions["A"].width = 30
    sheet.column_dimensions["B"].width = 18
    sheet.column_dimensions["C"].width = 15

    # Format data
    for row in range(2, sheet.max_row + 1):
        # Amount
        amount_cell = sheet[f"B{row}"]
        amount_cell.number_format = "$#,##0.00"
        amount_cell.alignment = Alignment(horizontal="right")

        if amount_cell.value and amount_cell.value < 0:
            amount_cell.font = Font(color="DC3545")
        else:
            amount_cell.font = Font(color="28A745")

        # Percentage
        pct_cell = sheet[f"C{row}"]
        pct_cell.number_format = '0.0"%"'
        pct_cell.alignment = Alignment(horizontal="right")


def format_instructions_sheet(sheet):
    """Format How to Use sheet"""

    # Column widths
    sheet.column_dimensions["A"].width = 25
    sheet.column_dimensions["B"].width = 80

    # Format title (first row)
    sheet["A1"].font = Font(size=16, bold=True, color="168C54")
    sheet.merge_cells("A1:B1")

    # Format section headers (bold)
    for row in range(1, sheet.max_row + 1):
        cell = sheet[f"A{row}"]
        if cell.value and ":" in str(cell.value):
            cell.font = Font(bold=True, size=12, color="168C54")

        # Wrap text for details column
        sheet[f"B{row}"].alignment = Alignment(wrap_text=True, vertical="top")
