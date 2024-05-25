import os
import PyPDF2
import re
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams
from collections import Counter
from flask import Flask, request, render_template

# Configurar la carpeta de uploads
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Función para leer texto de un archivo PDF
def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

# Función para limpiar y tokenizar texto
def clean_and_tokenize(text):
    text = re.sub(r'\s+', ' ', text)  # Eliminar espacios en blanco extra
    text = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ ]', '', text)  # Eliminar caracteres no alfabéticos
    tokens = nltk.word_tokenize(text.lower())
    return tokens

# Función para calcular la riqueza léxica
def lexical_richness(tokens):
    unique_tokens = set(tokens)
    richness = len(unique_tokens) / len(tokens)
    return round(richness, 2)  # Limitar a 2 números decimales

# Función para calcular la similitud basada en n-gramas
def calculate_similarity(text1, text2, n=3):
    ngrams1 = list(ngrams(text1, n))
    ngrams2 = list(ngrams(text2, n))
    counter1 = Counter(ngrams1)
    counter2 = Counter(ngrams2)
    
    intersection = sum((counter1 & counter2).values())
    total = sum((counter1 | counter2).values())
    
    similarity = intersection / total if total != 0 else 0
    return round(similarity * 100, 2)  # Regresar como porcentaje y limitar a 2 números decimales

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1 and file2:
            # Guardar archivos temporalmente
            file1_path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
            file2_path = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
            file1.save(file1_path)
            file2.save(file2_path)
            
            try:
                # Leer y procesar textos
                text1 = read_pdf(file1_path)
                text2 = read_pdf(file2_path)
                tokens1 = clean_and_tokenize(text1)
                tokens2 = clean_and_tokenize(text2)
                
                # Calcular riqueza léxica
                richness1 = lexical_richness(tokens1)
                richness2 = lexical_richness(tokens2)
                
                # Calcular similitud de plagio
                similarity = calculate_similarity(tokens1, tokens2)
                
            finally:
                # Asegurarse de que los archivos se eliminen después de procesar
                try:
                    os.remove(file1_path)
                except FileNotFoundError:
                    pass
                try:
                    os.remove(file2_path)
                except FileNotFoundError:
                    pass
                
            return render_template('results.html', richness1=richness1, richness2=richness2, similarity=similarity)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
