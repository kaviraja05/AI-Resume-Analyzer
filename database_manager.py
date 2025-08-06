#!/usr/bin/env python3
"""
Database Manager for AI Resume Analyzer
This tool helps you view, manage, and clean your database
"""

import sqlite3
import pandas as pd
import os

def connect_db():
    """Connect to the database"""
    db_path = os.path.join('App', 'resume_analyzer.db')
    if not os.path.exists(db_path):
        print("❌ Database not found. Run the app first to create it.")
        return None
    return sqlite3.connect(db_path)

def view_all_users():
    """View all registered users"""
    conn = connect_db()
    if not conn:
        return
    
    try:
        df = pd.read_sql_query("SELECT * FROM users ORDER BY timestamp DESC", conn)
        if df.empty:
            print("📭 No users found in database.")
        else:
            print(f"👥 Found {len(df)} users:")
            print("=" * 80)
            for _, user in df.iterrows():
                print(f"📧 Email: {user['email']}")
                print(f"👤 Name: {user['name']}")
                print(f"📱 Mobile: {user['mobile']}")
                print(f"📊 Score: {user['resume_score']}")
                print(f"🎯 Field: {user['predicted_field']}")
                print(f"📅 Date: {user['timestamp']}")
                print("-" * 40)
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def view_all_feedback():
    """View all feedback"""
    conn = connect_db()
    if not conn:
        return
    
    try:
        df = pd.read_sql_query("SELECT * FROM feedback ORDER BY timestamp DESC", conn)
        if df.empty:
            print("📭 No feedback found in database.")
        else:
            print(f"💬 Found {len(df)} feedback entries:")
            print("=" * 80)
            for _, feedback in df.iterrows():
                print(f"📧 Email: {feedback['email']}")
                print(f"👤 Name: {feedback['name']}")
                print(f"⭐ Rating: {'⭐' * feedback['rating']} ({feedback['rating']}/5)")
                print(f"💭 Comments: {feedback['comments']}")
                print(f"📅 Date: {feedback['timestamp']}")
                print("-" * 40)
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def delete_all_users():
    """Delete all user data"""
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        deleted_count = cursor.rowcount
        conn.commit()
        print(f"✅ Deleted {deleted_count} users from database.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def delete_all_feedback():
    """Delete all feedback data"""
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM feedback")
        deleted_count = cursor.rowcount
        conn.commit()
        print(f"✅ Deleted {deleted_count} feedback entries from database.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def delete_specific_user():
    """Delete a specific user by email"""
    email = input("Enter email to delete: ").strip()
    if not email:
        print("❌ No email provided.")
        return
    
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        deleted_count = cursor.rowcount
        conn.commit()
        if deleted_count > 0:
            print(f"✅ Deleted user with email: {email}")
        else:
            print(f"❌ No user found with email: {email}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def reset_database():
    """Completely reset the database"""
    db_path = os.path.join('App', 'resume_analyzer.db')
    
    confirm = input("⚠️  Are you sure you want to delete ALL data? Type 'YES' to confirm: ")
    if confirm != 'YES':
        print("❌ Operation cancelled.")
        return
    
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Database completely reset! A new empty database will be created when you run the app.")
        else:
            print("❌ Database file not found.")
    except Exception as e:
        print(f"❌ Error: {e}")

def export_data():
    """Export all data to CSV files"""
    conn = connect_db()
    if not conn:
        return
    
    try:
        # Export users
        users_df = pd.read_sql_query("SELECT * FROM users", conn)
        if not users_df.empty:
            users_df.to_csv('exported_users.csv', index=False)
            print(f"✅ Exported {len(users_df)} users to 'exported_users.csv'")
        
        # Export feedback
        feedback_df = pd.read_sql_query("SELECT * FROM feedback", conn)
        if not feedback_df.empty:
            feedback_df.to_csv('exported_feedback.csv', index=False)
            print(f"✅ Exported {len(feedback_df)} feedback entries to 'exported_feedback.csv'")
        
        if users_df.empty and feedback_df.empty:
            print("📭 No data to export.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def main():
    print("🗄️  AI Resume Analyzer - Database Manager")
    print("=" * 50)
    
    while True:
        print("\n📋 Choose an option:")
        print("1. 👥 View all users")
        print("2. 💬 View all feedback")
        print("3. 🗑️  Delete all users")
        print("4. 🗑️  Delete all feedback")
        print("5. 🎯 Delete specific user")
        print("6. ⚠️  Reset entire database")
        print("7. 📤 Export data to CSV")
        print("8. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            view_all_users()
        elif choice == '2':
            view_all_feedback()
        elif choice == '3':
            delete_all_users()
        elif choice == '4':
            delete_all_feedback()
        elif choice == '5':
            delete_specific_user()
        elif choice == '6':
            reset_database()
        elif choice == '7':
            export_data()
        elif choice == '8':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
