import sqlite3

# Connect to the database
connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

cursor.execute('DROP TABLE IF EXISTS farmers')

# Create the farmers table with farmer_id, name, email, and password
cursor.execute('''
CREATE TABLE IF NOT EXISTS farmers (
    farmer_id INTEGER PRIMARY KEY, 
    name TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL, 
    password TEXT NOT NULL
)
''')

# Insert data into the users table
cursor.execute("INSERT INTO farmers VALUES ('101','Athul','athul@example.com', 'athul123')")
cursor.execute("INSERT INTO farmers VALUES ('102','Kiran','kiran@example.com', 'kiran123')")
cursor.execute("INSERT INTO farmers VALUES ('1013','Dileep','dileep@example.com', 'dileep123')")


# Drop the diseases table if it exists
cursor.execute('DROP TABLE IF EXISTS diseases')

# Create the diseases table with disease_id, disease_name, disease_preventions, disease_image, and disease_symptoms
cursor.execute('''
CREATE TABLE IF NOT EXISTS diseases (
    disease_id INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_name TEXT NOT NULL UNIQUE,
    disease_preventions TEXT NOT NULL,
    disease_symptoms TEXT,
    disease_image TEXT
);
''')


# Inserting values into the diseases table
diseases = [
    ("Cassava Bacterial Blight (CBB)", "Remove infected plants$Use resistant varieties$Apply appropriate insecticides", "Symptoms include yellowing leaves and dieback.", "path/to/cbb_image.jpg"),
    ("Cassava Brown Streak Disease (CBSD)", "Use clean planting material$Destroy infected plants", "Symptoms include brown streaks on leaves.", "path/to/cbsd_image.jpg"),
    ("Cassava Green Mottle (CGM)", "Remove infected plants$Use resistant varieties$Apply appropriate insecticides", "Symptoms include mottling and distortion of leaves.", "path/to/cgm_image.jpg"),
    ("Cassava Mosaic Disease (CMD)", "Use clean planting material$Destroy infected plants", "Symptoms include mosaic patterns on leaves.", "path/to/cmd_image.jpg"),
    ("Your Plant is Healthy!", "Plant is healthy! NO Prevention required", "No visible symptoms.", "path/to/healthy_image.jpg")
]

# Insert each disease into the table
for disease_name, prevention_methods, symptoms, image_path in diseases:
    cursor.execute("SELECT COUNT(*) FROM diseases WHERE disease_name = ?", (disease_name,))
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO diseases (disease_name, disease_preventions, disease_symptoms, disease_image)
        VALUES (?, ?, ?, ?)
        """, (disease_name, prevention_methods, symptoms, image_path))
    else:
        print(f"Disease '{disease_name}' already exists in the Database.")



# Create the AG_OFFICER table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS AG_OFFICER (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
''')

# Optionally clear the AG_OFFICER table to avoid duplicates
cursor.execute("DELETE FROM AG_OFFICER")

# Insert data into the AG_OFFICER table
cursor.execute("INSERT OR IGNORE INTO AG_OFFICER (name, email, password) VALUES ('Sruti', 'sruti@agoff.com', 'sruti123')")
cursor.execute("INSERT OR IGNORE INTO AG_OFFICER (name, email, password) VALUES ('Anju', 'anju@agoff.com', 'anju123')")

# Commit the changes
connection.commit()
connection.close()
