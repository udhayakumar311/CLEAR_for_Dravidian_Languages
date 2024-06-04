import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('analysis_results.db')
c = conn.cursor()

# Execute a SELECT query to fetch all rows from the table
c.execute('SELECT * FROM analysis_results')

# Fetch all rows and print them
rows = c.fetchall()
for row in rows:
    print(row)

# Close the connection
conn.close()
