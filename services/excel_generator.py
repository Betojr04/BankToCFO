from pathlib import Path
from typing import List, Dict
import pandas as pd
from openpyxl import load_workbook
from openpyxl.chart import BarChart, LineChart, Reference, PieChart
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from services.categorizer import get_category_summary, get_monthly_summary


def generate_cfo_pack(transactions: List[Dict], output_path: Path):
    """
    Generate Excel CFO Pack with multiple sheets:
    1. Clean Transactions
    2. Monthly Summary
    3. Category Breakdown
    4. Charts
    """
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # Sheet 1: Clean Transactions
        df_transactions = pd.DataFrame(transactions)
        df_transactions = df_transactions[['date', 'description', 'category', 'amount', 'type']]
        df_transactions = df_transactions.sort_values('date')
        df_transactions.to_excel(writer, sheet_name='Transactions', index=False)
        
        # Sheet 2: Monthly Summary
        monthly_summary = get_monthly_summary(transactions)
        df_monthly = pd.DataFrame.from_dict(monthly_summary, orient='index')
        df_monthly.index.name = 'Month'
        df_monthly = df_monthly.reset_index()
        df_monthly.to_excel(writer, sheet_name='Monthly Summary', index=False)
        
        # Sheet 3: Category Breakdown
        category_summary = get_category_summary(transactions)
        df_categories = pd.DataFrame([
            {'Category': cat, 'Amount': amt}
            for cat, amt in sorted(category_summary.items(), key=lambda x: abs(x[1]), reverse=True)
        ])
        df_categories.to_excel(writer, sheet_name='Category Breakdown', index=False)
    
    # Load workbook to add formatting and charts
    workbook = load_workbook(output_path)
    
    # Format Transactions sheet
    format_transactions_sheet(workbook['Transactions'])
    
    # Format Monthly Summary sheet and add chart
    format_monthly_sheet(workbook['Monthly Summary'])
    
    # Format Category Breakdown sheet and add chart
    format_category_sheet(workbook['Category Breakdown'])
    
    # Save final workbook
    workbook.save(output_path)


def format_transactions_sheet(sheet):
    """Format the Transactions sheet with professional styling"""
    
    # Header formatting
    header_fill = PatternFill(start_color="168C54", end_color="168C54", fill_type="solid")  # Teal
    header_font = Font(bold=True, color="FFFFFF", size=12)
    
    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Column widths
    sheet.column_dimensions['A'].width = 12  # Date
    sheet.column_dimensions['B'].width = 50  # Description
    sheet.column_dimensions['C'].width = 25  # Category
    sheet.column_dimensions['D'].width = 15  # Amount
    sheet.column_dimensions['E'].width = 10  # Type
    
    # Format amounts as currency
    for row in range(2, sheet.max_row + 1):
        amount_cell = sheet[f'D{row}']
        amount_cell.number_format = '$#,##0.00'
        
        # Color code: red for expenses, green for revenue
        if amount_cell.value and amount_cell.value < 0:
            amount_cell.font = Font(color="DC3545")  # Red
        else:
            amount_cell.font = Font(color="28A745")  # Green
    
    # Add borders
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    for row in sheet.iter_rows(min_row=1, max_row=sheet.max_row, max_col=5):
        for cell in row:
            cell.border = thin_border
    
    # Freeze top row
    sheet.freeze_panes = 'A2'


def format_monthly_sheet(sheet):
    """Format Monthly Summary sheet and add chart"""
    
    # Header formatting
    header_fill = PatternFill(start_color="168C54", end_color="168C54", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    
    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Column widths
    sheet.column_dimensions['A'].width = 12  # Month
    sheet.column_dimensions['B'].width = 15  # Revenue
    sheet.column_dimensions['C'].width = 15  # Expenses
    sheet.column_dimensions['D'].width = 15  # Net Income
    
    # Format currency
    for row in range(2, sheet.max_row + 1):
        for col in ['B', 'C', 'D']:
            cell = sheet[f'{col}{row}']
            cell.number_format = '$#,##0.00'
    
    # Add line chart
    if sheet.max_row > 1:
        chart = LineChart()
        chart.title = "Monthly Cash Flow"
        chart.style = 10
        chart.y_axis.title = 'Amount ($)'
        chart.x_axis.title = 'Month'
        chart.height = 10
        chart.width = 20
        
        # Data for chart
        data = Reference(sheet, min_col=2, min_row=1, max_row=sheet.max_row, max_col=4)
        cats = Reference(sheet, min_col=1, min_row=2, max_row=sheet.max_row)
        
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        # Add chart to sheet
        sheet.add_chart(chart, "F2")


def format_category_sheet(sheet):
    """Format Category Breakdown sheet and add chart"""
    
    # Header formatting
    header_fill = PatternFill(start_color="168C54", end_color="168C54", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    
    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Column widths
    sheet.column_dimensions['A'].width = 30  # Category
    sheet.column_dimensions['B'].width = 15  # Amount
    
    # Format currency
    for row in range(2, sheet.max_row + 1):
        amount_cell = sheet[f'B{row}']
        amount_cell.number_format = '$#,##0.00'
        
        # Color code
        if amount_cell.value and amount_cell.value < 0:
            amount_cell.font = Font(color="DC3545")
        else:
            amount_cell.font = Font(color="28A745")
    
    # Add bar chart (top 10 categories by absolute value)
    if sheet.max_row > 1:
        chart = BarChart()
        chart.type = "col"
        chart.title = "Spending by Category"
        chart.y_axis.title = 'Amount ($)'
        chart.height = 12
        chart.width = 20
        
        # Limit to top 10
        max_data_row = min(sheet.max_row, 11)
        
        data = Reference(sheet, min_col=2, min_row=1, max_row=max_data_row)
        cats = Reference(sheet, min_col=1, min_row=2, max_row=max_data_row)
        
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        
        sheet.add_chart(chart, "D2")
