import os
import PyPDF2
import re
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams
from collections import Counter
from flask import Flask, request, render_template, redirect, url_for
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

STATIC_FOLDER = 'static'
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

app.config['STATIC_FOLDER'] = STATIC_FOLDER 

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def clean_and_tokenize(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ ]', '', text)
    tokens = nltk.word_tokenize(text.lower())
    return tokens

def lexical_richness(tokens):
    unique_tokens = set(tokens)
    richness = len(unique_tokens) / len(tokens)
    return round(richness, 2)

def calculate_similarity(text1, text2, n=3):
    ngrams1 = list(ngrams(text1, n))
    ngrams2 = list(ngrams(text2, n))
    counter1 = Counter(ngrams1)
    counter2 = Counter(ngrams2)
    
    intersection = sum((counter1 & counter2).values())
    total = sum((counter1 | counter2).values())
    
    similarity = intersection / total if total != 0 else 0
    return round(similarity * 100, 2)

def generate_word_frequency_chart(tokens1, tokens2, color1='skyblue', color2='lightcoral', num_words=10):
    stop_words = set(stopwords.words('spanish'))
    filtered_words1 = [word for word in tokens1 if word not in stop_words]
    filtered_words2 = [word for word in tokens2 if word not in stop_words]
    
    word_freq1 = Counter(filtered_words1)
    word_freq2 = Counter(filtered_words2)
    
    filtered_word_freq1 = {word: freq for word, freq in word_freq1.items() if len(word) > 3}
    filtered_word_freq2 = {word: freq for word, freq in word_freq2.items() if len(word) > 3}
    
    top_words1 = dict(sorted(filtered_word_freq1.items(), key=lambda item: item[1], reverse=True)[:num_words])
    top_words2 = dict(sorted(filtered_word_freq2.items(), key=lambda item: item[1], reverse=True)[:num_words])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.35
    index = range(num_words)
    ax.barh(index, list(top_words1.values()), bar_width, color=color1, label='Archivo 1')
    ax.barh([i + bar_width for i in index], list(top_words2.values()), bar_width, color=color2, label='Archivo 2')
    ax.set_ylabel('Palabras')
    ax.set_xlabel('Frecuencia')
    ax.set_title('Comparación de palabras más comunes')
    ax.set_yticks([i + bar_width / 2 for i in index])
    ax.set_yticklabels(list(top_words1.keys()))
    ax.legend()

    graph_path = os.path.join(app.config['STATIC_FOLDER'], 'word_frequency_chart.png')
    plt.savefig(graph_path)

    return graph_path

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1 and file2:
            file1_path = os.path.join(app.config['STATIC_FOLDER'], file1.filename)
            file2_path = os.path.join(app.config['STATIC_FOLDER'], file2.filename)
            file1.save(file1_path)
            file2.save(file2_path)
            
            try:
                text1 = read_pdf(file1_path)
                text2 = read_pdf(file2_path)
                tokens1 = clean_and_tokenize(text1)
                tokens2 = clean_and_tokenize(text2)
                
                richness1 = lexical_richness(tokens1)
                richness2 = lexical_richness(tokens2)
                
                similarity = calculate_similarity(tokens1, tokens2)
                
                graph_path = generate_word_frequency_chart(tokens1, tokens2)
                
            finally:
                try:
                    os.remove(file1_path)
                except FileNotFoundError:
                    pass
                try:
                    os.remove(file2_path)
                except FileNotFoundError:
                    pass
                
            return render_template('results.html', richness1=richness1, richness2=richness2, similarity=similarity, graph_path=graph_path)
    return render_template('upload.html')

@app.route('/back', methods=['GET', 'POST'])
def back():
    graph_path = os.path.join(app.config['STATIC_FOLDER'], 'word_frequency_chart.png')
    if os.path.exists(graph_path):
        os.remove(graph_path)
    return redirect(url_for('upload_files'))

if __name__ == '__main__':
    app.run(debug=True)
