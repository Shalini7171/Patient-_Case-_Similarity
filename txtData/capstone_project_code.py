# -*- coding: utf-8 -*-
"""capstone_project_code.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1OKfGIS9anXTPJAnw046Lt5_QexDn6boO
"""

# Install necessary libraries
!pip install flask pandas scikit-learn matplotlib

# Import required modules
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from flask import Flask, request, jsonify, render_template_string
from google.colab.output import eval_js
import matplotlib.pyplot as plt
import io
import base64

# Load the uploaded dataset
file_path = '/mnt/data/Diseases_Symptoms.csv'
dataset = pd.read_csv('/content/Diseases_Symptoms.csv')

# Preprocessing
# Using Symptoms column for similarity calculation
tfidf = TfidfVectorizer()
features = tfidf.fit_transform(dataset['Symptoms'])

# Build a similarity model using KNN
model = NearestNeighbors(n_neighbors=3, metric='cosine').fit(features)

# Create Flask App
app = Flask(_name_)

# Home Page Template
home_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Disease Similarity Finder</title>
</head>
<body>
    <h1>Find Similar Diseases</h1>
    <form action="/search" method="post">
        <label for="disease">Enter Disease or Symptom:</label><br>
        <input type="text" id="disease" name="disease" required><br><br>
        <button type="submit">Search</button>
    </form>
    <br>
    <div>
        {{ result|safe }}
    </div>
</body>
</html>
"""

# Helper function to plot results
def plot_results(query, similar_cases):
    fig, ax = plt.subplots()
    diseases = [query] + [x for x in similar_cases]
    values = [1] * len(diseases)
    ax.barh(diseases, values, color='skyblue')
    ax.set_xlabel('Similarity')
    ax.set_title('Similar Diseases')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return f'<img src="data:image/png;base64,{img_base64}" />'

@app.route('/', methods=['GET'])
def home():
    return render_template_string(home_page)

@app.route('/search', methods=['POST'])
def search():
    query = request.form['disease']
    query_vector = tfidf.transform([query])
    distances, indices = model.kneighbors(query_vector)
    similar_cases = dataset.iloc[indices[0]]

    result_lines = [f"<strong>Similar Cases for:</strong> {query}"]
    for _, row in similar_cases.iterrows():
        result_lines.append(f"<ul>")
        result_lines.append(f"<li><strong>Disease Name:</strong> {row['Name']}</li>")
        result_lines.append(f"<li><strong>Symptoms:</strong> {row['Symptoms']}</li>")
        result_lines.append(f"<li><strong>Treatments:</strong> {row['Treatments']}</li>")
        result_lines.append(f"</ul>")

    result_html = "<br>".join(result_lines)

    # Add graph
    result_html += plot_results(query, similar_cases['Name'].tolist())

    return render_template_string(home_page, result=result_html)

# Run the app
if _name_ == '_main_':
    url = eval_js("google.colab.kernel.proxyPort(5000)")
    print(f"Open the app in your browser: {url}")
    app.run(host='0.0.0.0', port=5000)