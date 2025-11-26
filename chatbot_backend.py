import flask
from flask import Flask, request, jsonify, render_template
import json 
import random 
import pickle 
import numpy as np 
import nltk
from nltk.stem import WordNetLemmatizer 
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.linear_model import LogisticRegression
import os

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, template_folder='templates', static_folder='static')
#runs server
'''app = Flask(__name__)'''
#Downloads needed NLTK at startup
nltk.download('punkt_tab', quiet=True)
nltk.download('wordnet', quiet=True)
 
lemmatizer = WordNetLemmatizer()
ignore_letters = ['?', '!', '.', ',']

def custom_tokenizer(txt):
    return [lemmatizer.lemmatize(w.lower()) for w in nltk.word_tokenize(txt) if w not in ignore_letters]

def train_model(): 
    with open('QA_intents.json') as file:
        intents = json.load(file)
 
    words = []
    classes = []
    documents = []
 
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            word_list = nltk.word_tokenize(pattern)
            words.extend(word_list)
            documents.append((word_list, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])
 
    words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_letters]
    words = sorted(list(set(words)))
    classes = sorted(list(set(classes)))
 
    pickle.dump(words, open('words.pkl', 'wb'))
    pickle.dump(classes, open('classes.pkl', 'wb'))
 
    corpus = [" ".join(doc[0]) for doc in documents]
    tags = [doc[1] for doc in documents]
 
    vectorizer = TfidfVectorizer(tokenizer=custom_tokenizer)
    X = vectorizer.fit_transform(corpus)
    y = np.array(tags)
 
    model = LogisticRegression(random_state=42, max_iter=200)
    model.fit(X, y)
 
    pickle.dump(model, open('chatbot_model.pkl', 'wb'))
    pickle.dump(vectorizer, open('vectorizer.pkl', 'wb'))
 
    print("Training is complete! Model and necessary files are saved.")
    return intents

def initialize_chatbot():
    if not os.path.exists('chatbot_model.pkl'):
        print("Model not found. Training model...")
        nltk.download('punkt', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        return train_model()
    else:
        with open('QA_intents.json') as file:
            return json.load(file)
#running on a server
'''intents_data = initialize_chatbot()
model = pickle.load(open('chatbot_model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))'''
#running locally
try:
    intents_data = initialize_chatbot()
    model = pickle.load(open('chatbot_model.pkl', 'rb'))
    vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
except Exception as e:
    print(f"Error loading chatbot: {str(e)}")
    raise

def get_chatbot_response(user_input):
    try:
        user_input_vec = vectorizer.transform([user_input])
        prediction = model.predict(user_input_vec)[0]
            
        for intent in intents_data['intents']:
            if intent['tag'] == prediction:
                response = random.choice(intent['responses'])
                return response
            
        return "I'm not sure how to respond to that, but I'm still learning."
    except Exception as e:
        print(f"Error in get_chatbot_response: {str(e)}")
        raise
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("Chatbot_window.html")

@app.route("/get")
def get_response():
    user_message = request.args.get('msg')
    if user_message:
        return get_chatbot_response(user_message)
    return "No message received"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
