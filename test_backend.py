"""
Test script to verify BankToCFO backend functionality
"""

import sys
from pathlib import Path

# Test 1: Import all modules
print("Test 1: Importing modules...")
try:
    from services.parser import parse_bank_statement
    from services.categorizer import categorize_transactions, get_monthly_summary, get_category_summary
    from services.excel_generator import generate_cfo_pack
    print("✅ All modules imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Test categorizer
print("\nTest 2: Testing categorizer...")
try:
    test_transactions = [
        {
            'date': '2024-01-15',
            'description': 'Amazon Web Services',
            'amount': -50.00,
            'type': 'Debit'
        },
        {
            'date': '2024-01-16',
            'description': 'Customer Payment via Stripe',
            'amount': 1500.00,
            'type': 'Credit'
        },
        {
            'date': '2024-01-17',
            'description': 'Starbucks Coffee',
            'amount': -5.50,
            'type': 'Debit'
        }
    ]
    
    categorized = categorize_transactions(test_transactions)
    
    assert categorized[0]['category'] == 'Software', f"Expected 'Software', got {categorized[0]['category']}"
    assert categorized[1]['category'] == 'Revenue', f"Expected 'Revenue', got {categorized[1]['category']}"
    assert categorized[2]['category'] == 'Meals', f"Expected 'Meals', got {categorized[2]['category']}"
    
    print("✅ Categorization working correctly")
except Exception as e:
    print(f"❌ Categorization failed: {e}")
    sys.exit(1)

# Test 3: Test monthly summary
print("\nTest 3: Testing monthly summary...")
try:
    monthly = get_monthly_summary(categorized)
    assert '2024-01' in monthly
    assert monthly['2024-01']['revenue'] == 1500.00
    assert monthly['2024-01']['expenses'] == 55.50
    assert monthly['2024-01']['net_income'] == 1444.50
    
    print("✅ Monthly summary working correctly")
except Exception as e:
    print(f"❌ Monthly summary failed: {e}")
    sys.exit(1)

# Test 4: Test category summary
print("\nTest 4: Testing category summary...")
try:
    categories = get_category_summary(categorized)
    assert 'Software' in categories
    assert 'Revenue' in categories
    assert 'Meals' in categories
    
    print("✅ Category summary working correctly")
except Exception as e:
    print(f"❌ Category summary failed: {e}")
    sys.exit(1)

# Test 5: Test Excel generation
print("\nTest 5: Testing Excel generation...")
try:
    test_output = Path("test_cfo_pack.xlsx")
    generate_cfo_pack(categorized, test_output)
    
    assert test_output.exists(), "Excel file was not created"
    assert test_output.stat().st_size > 0, "Excel file is empty"
    
    # Clean up
    test_output.unlink()
    
    print("✅ Excel generation working correctly")
except Exception as e:
    print(f"❌ Excel generation failed: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✅ ALL TESTS PASSED!")
print("="*50)
print("\nBackend is ready to deploy!")
print("\nNext steps:")
print("1. Set your OPENAI_API_KEY in .env file")
print("2. Test locally: python main.py")
print("3. Deploy to Railway")
print("4. Update Lovable frontend with backend URL")
