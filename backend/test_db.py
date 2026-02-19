"""
Database Connection Test for Your Resume Analyzer Project
Run this to verify MS SQL Server setup is working
"""

import sys
import os

# Make sure we can import from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if required packages are installed"""
    print("\n" + "="*60)
    print("TEST 1: Checking Required Packages")
    print("="*60)
    
    try:
        import pyodbc
        print("✅ pyodbc installed")
        
        # List available drivers
        drivers = pyodbc.drivers()
        print(f"\n📊 Found {len(drivers)} ODBC drivers:")
        for driver in drivers:
            print(f"  - {driver}")
            if 'SQL Server' in driver:
                print("    ← This one will be used!")
        
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("\n💡 Fix: Run 'pip install pyodbc'")
        return False

def test_database_module():
    """Test if database module can be imported"""
    print("\n" + "="*60)
    print("TEST 2: Testing Database Module")
    print("="*60)
    
    try:
        from database import Database
        print("✅ database.py imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing database.py: {e}")
        print("\n💡 Fix: Make sure database.py is in the same folder")
        return False

def test_database_connection():
    """Test database connection and initialization"""
    print("\n" + "="*60)
    print("TEST 3: Testing Database Connection")
    print("="*60)
    
    try:
        from database import Database
        
        print("Initializing database...")
        db = Database()
        print("✅ Database initialized successfully!")
        
        # Test getting questions
        print("\n" + "="*60)
        print("TEST 4: Testing Database Operations")
        print("="*60)
        
        print("Fetching questions for 'Data Scientist'...")
        questions = db.get_questions_by_role('Data Scientist', limit=5)
        print(f"✅ Retrieved {len(questions)} questions")
        
        if questions:
            print("\n📝 Sample Question:")
            q = questions[0]
            print(f"  Question: {q['question'][:60]}...")
            print(f"  Options: {len(q['options'])} choices")
            print(f"  Difficulty: {q['difficulty']}")
            print(f"  Has explanation: {'Yes' if q['explanation'] else 'No'}")
        
        # Test adding and retrieving
        print("\n" + "="*60)
        print("TEST 5: Testing Add/Retrieve")
        print("="*60)
        
        print("Adding test question...")
        db.add_question(
            job_role='Test Role',
            question='This is a test question?',
            options=['A', 'B', 'C', 'D'],
            correct_answer='A',
            difficulty='easy',
            explanation='This is a test explanation.'
        )
        print("✅ Question added")
        
        print("Retrieving test question...")
        test_questions = db.get_questions_by_role('Test Role', limit=1)
        if test_questions:
            print(f"✅ Retrieved test question: {test_questions[0]['question'][:40]}...")
        
        return True
        
    except Exception as e:
        print("❌ Database operation failed!")
        print(f"Error: {e}")
        print("\n💡 Common fixes:")
        print("  1. Check if SQL Server is running (services.msc)")
        print("  2. Verify server name in config_db.py")
        print("  3. Try Windows Authentication (use_windows_auth=True)")
        print("  4. Check if ODBC Driver 17 is installed")
        return False

def test_full_workflow():
    """Test the complete MCQ workflow"""
    print("\n" + "="*60)
    print("TEST 6: Complete Workflow Test")
    print("="*60)
    
    try:
        from database import Database
        
        db = Database()
        
        # Simulate a test session
        print("1. Getting questions for Web Developer...")
        questions = db.get_questions_by_role('Web Developer', limit=3)
        print(f"   ✅ Got {len(questions)} questions")
        
        # Simulate answering
        print("\n2. Simulating test answers...")
        test_answers = {}
        for q in questions:
            # For testing, just pick the correct answer
            test_answers[str(q['id'])] = q['correct_answer']
        print(f"   ✅ Generated {len(test_answers)} answers")
        
        # Evaluate (manually, not through API)
        print("\n3. Evaluating answers...")
        correct = 0
        for q in questions:
            if test_answers.get(str(q['id'])) == q['correct_answer']:
                correct += 1
        
        score = (correct / len(questions)) * 100
        print(f"   ✅ Score: {score}% ({correct}/{len(questions)} correct)")
        
        # Save result
        print("\n4. Saving test result...")
        result = {
            'job_role': 'Web Developer',
            'total_questions': len(questions),
            'correct_answers': correct,
            'score_percentage': score
        }
        db.save_test_result(result)
        print("   ✅ Result saved")
        
        # Get history
        print("\n5. Retrieving test history...")
        history = db.get_test_history(limit=3)
        print(f"   ✅ Found {len(history)} test results")
        
        if history:
            print("\n   Latest result:")
            latest = history[0]
            print(f"   - Role: {latest['job_role']}")
            print(f"   - Score: {latest['score_percentage']}%")
            print(f"   - Date: {latest['timestamp']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   RESUME ANALYZER - DATABASE CONNECTION TEST SUITE          ║
║                                                              ║
║   This will verify your MS SQL Server setup is working      ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Test 1: Imports
    results.append(("Package Installation", test_imports()))
    
    # Test 2: Module
    if results[-1][1]:
        results.append(("Database Module", test_database_module()))
    else:
        print("\n⚠️ Skipping remaining tests due to missing packages")
        return
    
    # Test 3-5: Database operations
    if results[-1][1]:
        results.append(("Database Operations", test_database_connection()))
    else:
        print("\n⚠️ Skipping remaining tests due to module import failure")
        return
    
    # Test 6: Workflow
    if results[-1][1]:
        results.append(("Complete Workflow", test_full_workflow()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📈 Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\nYour database is ready to use!")
        print("\nNext steps:")
        print("1. Run your Flask app: python app.py")
        print("2. Test the MCQ endpoints")
        print("3. Build your frontend")
    else:
        print("\n" + "="*60)
        print("⚠️ SOME TESTS FAILED")
        print("="*60)
        print("\nPlease fix the errors above before proceeding.")
        print("\nCommon fixes:")
        print("- Install pyodbc: pip install pyodbc")
        print("- Check SQL Server is running")
        print("- Verify config_db.py settings")
        print("- Try Windows Authentication")

if __name__ == '__main__':
    run_all_tests()