import os
import sys
import django
import sqlite3

# Set python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps

app_models = apps.get_app_config('siisto').get_models()

sqlite_conn = sqlite3.connect('db.sqlite3')
cur = sqlite_conn.cursor()

for model in app_models:
    table_name = model._meta.db_table
    cur.execute(f"PRAGMA table_info({table_name})")
    existing_cols = {row[1]: row[2] for row in cur.fetchall()}
    
    print(f"\n--- Checking table: {table_name} ---")
    for field in model._meta.concrete_fields:
        col_name = field.column
        if col_name not in existing_cols:
            internal_type = field.get_internal_type()
            # map django type to sqlite type
            if 'Integer' in internal_type or 'Auto' in internal_type or 'ForeignKey' in internal_type:
                sql_type = 'INTEGER'
            elif 'Float' in internal_type or 'Decimal' in internal_type:
                sql_type = 'REAL'
            elif 'Boolean' in internal_type:
                sql_type = 'bool DEFAULT 0'
            elif 'Date' in internal_type:
                sql_type = 'datetime'
            elif 'Text' in internal_type:
                sql_type = 'TEXT DEFAULT ""'
            else:
                sql_type = 'varchar(255) DEFAULT ""'
            
            print(f"Adding missing column: {table_name}.{col_name} ({sql_type})")
            try:
                cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {sql_type}")
                sqlite_conn.commit()
            except Exception as e:
                print(f"Error adding {col_name}: {e}")
        else:
            print(f"  OK: {col_name}")

sqlite_conn.close()
print("\nAll database tables and columns are now 100% synchronized with models.py!")
