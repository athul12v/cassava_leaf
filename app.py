from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import sqlite3
import dis
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
# from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
import numpy as np
import io
import tensorflow_hub as hub

#this is the original project.

app = Flask(__name__)
# model = load_model("D:\Models\final_model\final_model.h5")
#the below is the old_model i trained.
# model = load_model(r"D:\Models\final_model\final_model.h5")
classifier = hub.KerasLayer('https://kaggle.com/models/google/cropnet/frameworks/TensorFlow2/variations/classifier-cassava-disease-v1/versions/1')
label_classes = ['0', '1', '2', '3', '4']

diseases = [
    ("Cassava Bacterial Blight (CBB)", "Remove infected plants$Use resistant varieties$Apply appropriate insecticides"),
    ("Cassava Brown Streak Disease (CBSD)", "Use clean planting material$Destroy infected plants"),
    ("Cassava Green Mottle (CGM)", "Remove infected plants$Use resistant varieties$Apply appropriate insecticides"),
    ("Cassava Mosaic Disease (CMD)", "Use clean planting material$Destroy infected plants"),
    ("Your Plant is Healthy!", "Plant is healthy! NO Prevention required")
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        email = request.form['email']
        password = request.form['password']

        # Check in AG_OFFICER table
        cursor.execute("SELECT * FROM AG_OFFICER WHERE email = ? AND password = ?", (email, password))
        ag_officer = cursor.fetchone()

        # Check in users table
        cursor.execute("SELECT * FROM farmers WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()

        connection.close()

        if ag_officer:
            return render_template('ag_off.html')  # Redirect to AG Officer Dashboard
        elif user:
            return render_template('index.html')  # Redirect to Farmer Dashboard
        else:
            print('Incorrect Credentials! Please try again.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Check if email already exists for both Farmers and AG Officers
        if role == 'FARMER':
            query = "SELECT * FROM farmers WHERE email = ?"
            cursor.execute(query, (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                print('Email already registered as a Farmer. Please use a different email or login.')
                return redirect(url_for('create_account'))
            else:
                # Insert new farmer into the database
                cursor.execute("INSERT INTO farmers (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                connection.commit()

        elif role == 'AG_OFFICER':
            query = "SELECT * FROM AG_OFFICER WHERE email = ?"
            cursor.execute(query, (email,))
            existing_officer = cursor.fetchone()

            if existing_officer:
                print('Email already registered as an AG Officer. Please use a different email or login.')
                return redirect(url_for('create_account'))
            else:
                # Insert new AG Officer into the database
                cursor.execute("INSERT INTO AG_OFFICER (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                connection.commit()

        connection.close()

        print('Account created successfully! Please login.')
        return redirect(url_for('login'))

    return render_template('create_account.html')

@app.route('/pred', methods=['POST'])
def predict():
    file = request.files.get('file')

    if not file:
        return render_template('result.html', error='No file uploaded.')

    try:
        # Convert FileStorage to io.BytesIO
        img_bytes = io.BytesIO(file.read())
        
        # Load and preprocess the image
        img = image.load_img(img_bytes, target_size=(224, 224))
        img = image.img_to_array(img)
        img = tf.cast(img, tf.float32) / 255.0  # Normalize the image
        
        # Expand dimensions to match model input shape
        img_arr = np.expand_dims(img, axis=0)

        # Make prediction
        probabilities = classifier(img_arr)  # Using the TensorFlow Hub model
        predictions = tf.argmax(probabilities, axis=-1).numpy()  # Convert to numpy array
        predicted_label = str(predictions[0])  # Ensure this is a string to match `label_classes`
    
        # Fetch disease information from the database
        query = "SELECT disease_name, disease_preventions FROM diseases WHERE disease_id = ?"
        with sqlite3.connect('user_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute(query, (predicted_label,))
            disease_info = cursor.fetchone()

        if disease_info:
            disease_name, prevention_methods = disease_info
            prevention_list = prevention_methods.split('$')  # Split prevention methods
            return render_template('result.html', disease=disease_name, prevention=prevention_list)
        else:
            return render_template('result.html', error='No disease information found in the database.')

    except Exception as e:
        print(f"Error Occurred: {str(e)}")
        return render_template('result.html', error='An error occurred during prediction.', details=str(e))

@app.route('/logout')
def logout():
    # session.clear()  
    return redirect(url_for('login'))  

@app.route('/user_view')
def view_diseases_for_farmers():
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()
    
    # Fetch all diseases from the database
    cursor.execute("SELECT disease_id, disease_name, disease_preventions, disease_symptoms, disease_image FROM diseases")
    diseases = cursor.fetchall()
    
    # Debugging: Print the fetched diseases
    print("Fetched Diseases:", diseases)  # This will print to your console
    
    connection.close()
    return render_template('user_view.html', diseases=diseases)  

@app.route('/view_diseases')
def view_diseases_for_ag():
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()
    
    # Fetch all diseases from the database
    cursor.execute("SELECT disease_id, disease_name, disease_preventions, disease_symptoms, disease_image FROM diseases")
    diseases = cursor.fetchall()
    
    # Debugging: Print the fetched diseases
    print("Fetched Diseases:", diseases)  # This will print to your console
    
    connection.close()
    return render_template('view_disease.html', diseases=diseases)

@app.route('/add_disease', methods=['GET', 'POST'])
def add_disease():
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()

    if request.method == 'POST':
        disease_name = request.form['disease_name']
        prevention_methods = request.form['prevention_methods'].replace('\n', '$')
        symptoms = request.form['symptoms']
        disease_image = request.form['disease_image']

        # Check for existing disease
        cursor.execute("SELECT COUNT(*) FROM diseases WHERE disease_name = ?", (disease_name,))
        if cursor.fetchone()[0] > 0:
            connection.close()
            return render_template('add_disease.html', error='Disease already exists.')

        # Insert the new disease
        cursor.execute("""INSERT INTO diseases (disease_name, disease_preventions, disease_symptoms, disease_image)
                          VALUES (?, ?, ?, ?)""", 
                       (disease_name, prevention_methods, symptoms, disease_image))
        connection.commit()
        connection.close()

        return redirect(url_for('view_diseases_for_ag'))

    connection.close()
    return render_template('add_disease.html')

@app.route('/modify_disease/<int:disease_id>', methods=['GET', 'POST'])
def modify_disease(disease_id):
    try:
        with sqlite3.connect('user_data.db') as connection:
            cursor = connection.cursor()
            if request.method == 'POST':
                disease_name = request.form['disease_name']
                prevention_methods = request.form['prevention_methods'].replace('\n', '$')
                symptoms = request.form['symptoms']
                disease_image = request.form['disease_image']

                # Check if the disease name already exists
                cursor.execute("SELECT COUNT(*) FROM diseases WHERE disease_name = ? AND disease_id != ?", 
                               (disease_name, disease_id))
                if cursor.fetchone()[0] > 0:
                    cursor.execute("SELECT * FROM diseases WHERE disease_id = ?", (disease_id,))
                    disease = cursor.fetchone()
                    return render_template('modify_disease.html', disease=disease, error='Disease name already exists.')

                # Update the disease
                cursor.execute(""" 
                    UPDATE diseases 
                    SET disease_name = ?, disease_preventions = ?, disease_symptoms = ?, disease_image = ? 
                    WHERE disease_id = ?""", 
                    (disease_name, prevention_methods, symptoms, disease_image, disease_id))
                connection.commit()

                print("Redirecting to view_diseases")  # Debugging statement
                return redirect(url_for('view_diseases_for_ag'))

            # GET method
            cursor.execute("SELECT * FROM diseases WHERE disease_id = ?", (disease_id,))
            disease = cursor.fetchone()
        
        return render_template('modify_disease.html', disease=disease)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return render_template('modify_disease.html', error='Database error occurred.')

@app.route('/delete_disease/<int:disease_id>', methods=['POST'])
def delete_disease(disease_id):
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM diseases WHERE disease_id = ?", (disease_id,))
    connection.commit()
    connection.close()
    return redirect(url_for('view_diseases_for_ag'))


if __name__ == '__main__':
    app.run(debug=True)   
