﻿# Cassava Leaf Disease Identification 
# A Deep Learning Approach
Here's a simple **README** for your GitHub project:

---

This project identifies diseases in cassava leaves using a deep learning model based on the pre-trained ResNet50 architecture. The project includes two user roles: Farmer and Agricultural Officer.

## Setup Instructions

1. **Install Required Libraries:**
   - TensorFlow (for deep learning)
   - Pillow (for image loading)
   - Flask (for the web framework)

   Run the following command to install them:
   ```bash
   pip install tensorflow pillow flask
   ```

2. **Database:**
   - The project uses SQLite3 as the database. No need for external setup.

3. **Run the Project:**
   - First, set up the database by running:
     ```bash
     python create.py
     ```
   - Then, start the application:
     ```bash
     python app.py
     ```

## Project Overview

- **Farmer Module:** Allows farmers to log in and upload images of cassava leaves for disease identification. The system predicts the disease and provides prevention methods.
  
- **Agricultural Officer Module:** Officers can log in to manage disease data, including adding new diseases and updating prevention methods.

## Abstract

Cassava plants are vital for food security in Africa, but viral diseases threaten crop yields. This project trains a CNN model on ~21k images to classify 4 disease types and healthy plants. Using transfer learning with ResNet50, we achieved a validation accuracy of ~86%. Future work could involve Test Time Augmentation and experimenting with larger image resolutions and other architectures.

