import sqlite3

conn = sqlite3.connect('cmo_ai.db')
cursor = conn.cursor()

# Check tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables:', tables)

# Check users
try:
    cursor.execute('SELECT id, email, full_name, hashed_password FROM user')
    users = cursor.fetchall()
    print('Users:', users)
except Exception as e:
    print('Error reading users:', e)

conn.close()
