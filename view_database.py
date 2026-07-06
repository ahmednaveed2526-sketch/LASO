# view_database.py - Database Inspector for LASO App
import sqlite3
import os
import sys

# Force UTF-8 output encoding for terminal formatting
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LASO - Back End', 'laso_app.db')

def inspect_db():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file not found at: {DB_PATH}")
        return

    print("=" * 65)
    print("      LASO APPLICATION - SQLITE DATABASE INSPECTOR")
    print("=" * 65)
    print(f"📁 Database Path: {DB_PATH}\n")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Get List of Tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    if not tables:
        print("⚠️ No tables found in the database.")
        conn.close()
        return

    print(f"📊 Found {len(tables)} Database Tables:")
    print("-" * 65)
    
    for table_name in tables:
        # Get count of rows
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        # Get schema details
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        col_summary = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
        
        print(f"🔹 Table: {table_name:<15} | Row Count: {row_count:<5}")
        print(f"   Columns: {col_summary}\n")

    # 2. Display Sample Records from each Table
    print("=" * 65)
    print("              SAMPLE RECORDS PREVIEW")
    print("=" * 65)

    for table_name in tables:
        print(f"\n📁 Table Content: {table_name.upper()}")
        print("-" * 65)
        
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cur.fetchall()

        if not rows:
            print("   (Empty Table - No records yet)")
            continue

        # Print Headers
        headers = rows[0].keys()
        header_line = " | ".join(headers)
        print(header_line)
        print("-" * len(header_line))

        # Print Rows
        for r in rows:
            print(" | ".join([str(val) for val in dict(r).values()]))
            
    conn.close()

if __name__ == '__main__':
    inspect_db()
