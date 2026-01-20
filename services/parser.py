import pandas as pd
from pathlib import Path
from typing import List, Dict
from datetime import datetime


def parse_bank_statement(file_path: Path) -> List[Dict]:
    """
    Main parser function that routes to PDF or CSV parser
    
    Returns:
        List of transaction dictionaries with keys:
        - date: YYYY-MM-DD string
        - description: Transaction description
        - amount: Float (negative for debits, positive for credits)
        - type: 'Debit' or 'Credit'
    """
    
    file_extension = file_path.suffix.lower()
    
    if file_extension == '.pdf':
        from services.pdf_parser import parse_pdf_statement
        return parse_pdf_statement(file_path)
    
    elif file_extension == '.csv':
        return parse_csv_statement(file_path)
    
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")


def parse_csv_statement(file_path: Path) -> List[Dict]:
    """Parse CSV bank statements"""
    
    try:
        # Read CSV - try different encodings
        try:
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin1')
        
        # Detect bank format
        bank_format = detect_bank_format(df)
        
        # Parse based on format
        if bank_format == 'chase':
            return parse_chase_format(df)
        elif bank_format == 'bofa':
            return parse_bofa_format(df)
        elif bank_format == 'wells_fargo':
            return parse_wells_fargo_format(df)
        elif bank_format == 'generic':
            return parse_generic_format(df)
        else:
            raise ValueError("Unknown CSV format - unable to detect bank")
            
    except Exception as e:
        raise ValueError(f"Failed to parse CSV: {str(e)}")


def detect_bank_format(df: pd.DataFrame) -> str:
    """
    Detect which bank format the CSV is in based on column names
    """
    columns = [col.lower() for col in df.columns]
    
    # Chase bank format
    if 'posting date' in columns and 'description' in columns:
        return 'chase'
    
    # Bank of America format
    if 'posted date' in columns and 'payee' in columns:
        return 'bofa'
    
    # Wells Fargo format
    if 'date' in columns and 'amount' in columns:
        return 'wells_fargo'
    
    # Generic format (Date, Description, Amount)
    if 'date' in columns and 'description' in columns and 'amount' in columns:
        return 'generic'
    
    return 'unknown'


def parse_chase_format(df: pd.DataFrame) -> List[Dict]:
    """Parse Chase bank CSV format"""
    transactions = []
    
    for _, row in df.iterrows():
        try:
            # Chase format: Posting Date, Description, Amount, Type, Balance
            transaction = {
                'date': pd.to_datetime(row['Posting Date']).strftime('%Y-%m-%d'),
                'description': str(row['Description']).strip(),
                'amount': float(row['Amount']),
                'type': str(row.get('Type', 'Unknown')),
            }
            transactions.append(transaction)
        except Exception as e:
            # Skip malformed rows
            continue
    
    return transactions


def parse_bofa_format(df: pd.DataFrame) -> List[Dict]:
    """Parse Bank of America CSV format"""
    transactions = []
    
    for _, row in df.iterrows():
        try:
            # BofA format: Posted Date, Payee, Address, Amount
            amount = float(row['Amount'])
            transaction = {
                'date': pd.to_datetime(row['Posted Date']).strftime('%Y-%m-%d'),
                'description': str(row['Payee']).strip(),
                'amount': amount,
                'type': 'Debit' if amount < 0 else 'Credit',
            }
            transactions.append(transaction)
        except Exception as e:
            continue
    
    return transactions


def parse_wells_fargo_format(df: pd.DataFrame) -> List[Dict]:
    """Parse Wells Fargo CSV format"""
    transactions = []
    
    for _, row in df.iterrows():
        try:
            amount = float(row['Amount'])
            transaction = {
                'date': pd.to_datetime(row['Date']).strftime('%Y-%m-%d'),
                'description': str(row.get('Description', row.get('Memo', ''))).strip(),
                'amount': amount,
                'type': 'Debit' if amount < 0 else 'Credit',
            }
            transactions.append(transaction)
        except Exception as e:
            continue
    
    return transactions


def parse_generic_format(df: pd.DataFrame) -> List[Dict]:
    """Parse generic CSV format (Date, Description, Amount)"""
    transactions = []
    
    for _, row in df.iterrows():
        try:
            amount = float(row['Amount'])
            transaction = {
                'date': pd.to_datetime(row['Date']).strftime('%Y-%m-%d'),
                'description': str(row['Description']).strip(),
                'amount': amount,
                'type': 'Debit' if amount < 0 else 'Credit',
            }
            transactions.append(transaction)
        except Exception as e:
            continue
    
    return transactions
