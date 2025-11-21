import flask
from flask import Flask, request, jsonify, render_template
app = Flask(__name__)
import json 
import random 
import pickle 
import numpy as np 
import nltk 
from nltk.stem import WordNetLemmatizer 
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.linear_model import LogisticRegression
import tkinter as tk
 
# Global lemmatizer and tokenizer for pickling compatibility
lemmatizer = WordNetLemmatizer()
ignore_letters = ['?', '!', '.', ',']

def custom_tokenizer(txt):
    return [lemmatizer.lemmatize(w.lower()) for w in nltk.word_tokenize(txt) if w not in ignore_letters]

# ----------------- 
# 1. DATA PREP AND MODEL TRAINING 
# ----------------- 
def train_model(): 
    # Load the intents file 
    with open('QA_intents') as file:
        intents = json.load(file)
 
    words = []
    classes = []
    documents = []
 
    # Process each intent 
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            word_list = nltk.word_tokenize(pattern)
            words.extend(word_list)
            documents.append((word_list, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])
 
    # Lemmatize words, remove duplicates 
    words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_letters]
    words = sorted(list(set(words)))
    classes = sorted(list(set(classes)))
 
    # Save the processed words and classes 
    pickle.dump(words, open('words.pkl', 'wb'))
    pickle.dump(classes, open('classes.pkl', 'wb'))
 
    # Prepare documents for TF-IDF 
    corpus = [" ".join(doc[0]) for doc in documents]
    tags = [doc[1] for doc in documents]
 
    # Vectorize the corpus using the global custom_tokenizer
    vectorizer = TfidfVectorizer(tokenizer=custom_tokenizer)
    X = vectorizer.fit_transform(corpus)
    y = np.array(tags)
 
    # Train the Logistic Regression model 
    model = LogisticRegression(random_state=42, max_iter=200)
    model.fit(X, y)
 
    # Save the trained model and vectorizer 
    pickle.dump(model, open('chatbot_model.pkl', 'wb'))
    pickle.dump(vectorizer, open('vectorizer.pkl', 'wb'))
 
    print("Training is complete! Model and necessary files are saved.")
    return intents
 
# ----------------- 
# 2. CHATBOT INTERACTION 
# ----------------- 
def run_chatbot(intents):
    # Load the saved model, vectorizer, and classes 
    model = pickle.load(open('chatbot_model.pkl', 'rb'))
    vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))

    @app.route("/get")
    def get_response(user_input):
        # Transform user input 
        user_input_vec = vectorizer.transform([user_input])
        # Predict the tag 
        prediction = model.predict(user_input_vec)[0]
         
        # Get a random response from the predicted tag 
        for intent in intents['intents']:
            if intent['tag'] == prediction:
                response = random.choice(intent['responses'])
                return response
         
        return "I'm not sure how to respond to that, but I'm still learning."
 
    # Main chat loop 
    print("\nChatbot is live! Type 'quit' to exit.")
    while True:
        message = input("You: ")
        if message.lower() == 'quit':
            break
         
        response = get_response(message)
        print(f"Bot: {response}")

#-----------------
# FLASK WEB INTERFACE
#-----------------
@app.route("/")
def home():
    return render_template("Chatbot_window")  # Serve the chat UI window
 
# ----------------- 
# MAIN EXECUTION 
# ----------------- 
if __name__ == "__main__":
    #ti run debug
    app.run(debug=True)
    trained_intents = train_model()
    run_chatbot(trained_intents)