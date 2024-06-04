import sqlite3

# Connect to SQLite database (creates if not exists)
conn = sqlite3.connect('analysis_results.db')
cursor = conn.cursor()

# Create a table to store analysis results
cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE,
        time TIME,
        text TEXT,
        language TEXT,
        num_characters INTEGER,
        num_words INTEGER,
        num_sentences INTEGER,
        num_characters_100_words INTEGER,
        num_sentences_per_100_words INTEGER,
        total_syllable_count INTEGER,
        monosyllabic_words_count INTEGER,
        polysyllabic_words_count INTEGER,
        ARI REAL,
        CLI REAL,
        FRE REAL,
        FKGL REAL,
        GFI REAL,
        SMOG REAL,
        FORCAST REAL,
        personalized_index REAL
    )
''')

# Commit changes and close connection
conn.commit()
conn.close()
