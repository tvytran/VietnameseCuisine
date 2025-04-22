# Project Structure
# app.py - Main Flask application
# static/ - Static files (CSS, JS, images)
# templates/ - HTML templates
# data/ - JSON data files

# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os
import datetime

app = Flask(__name__)
app.secret_key = 'vietnamese_cuisine_app_secret_key'

# Load data from JSON files
def load_data():
    with open('data/regions.json', 'r') as f:
        regions = json.load(f)
    with open('data/dishes.json', 'r') as f:
        dishes = json.load(f)
    with open('data/quiz.json', 'r') as f:
        quiz = json.load(f)
    with open('data/history.json', 'r') as f:
        history = json.load(f)
    return regions, dishes, quiz, history

# Initialize user data
def init_user():
    if 'user_data' not in session:
        session['user_data'] = {
            'start_time': datetime.datetime.now().isoformat(),
            'pages_visited': [],
            'quiz_answers': [],
            'score': 0
        }
    return session['user_data']

# Record page visit
def record_page_visit(page_name):
    user_data = init_user()
    user_data['pages_visited'].append({
        'page': page_name,
        'time': datetime.datetime.now().isoformat()
    })
    session['user_data'] = user_data

# Home route
@app.route('/')
def home():
    # Reset user data when visiting home
    if 'user_data' in session:
        session.pop('user_data', None)
    record_page_visit('home')
    return render_template('index.html')

# General Vietnamese cuisine info route
@app.route('/general')
def general():
    regions, dishes, quiz, history = load_data()
    record_page_visit('general')
    return render_template('general.html', regions=regions)

# Learn route with variable for lesson number
@app.route('/learn/<int:lesson_id>')
def learn(lesson_id):
    regions, dishes, quiz, history = load_data()
    
    if lesson_id <= 0 or lesson_id > len(regions):
        return redirect(url_for('home'))
    
    region = regions[lesson_id - 1]
    record_page_visit(f'learn/{lesson_id}')
    
    next_lesson = lesson_id + 1 if lesson_id < len(regions) else None
    
    return render_template('learn.html', 
                          region=region, 
                          lesson_id=lesson_id, 
                          next_lesson=next_lesson)

# Dish comparison route
@app.route('/compare/<dish_name>')
def compare_dish(dish_name):
    regions, dishes, quiz, history = load_data()
    
    # Find the dish by name
    dish = next((d for d in dishes if d['name'].lower() == dish_name.lower()), None)
    
    if not dish:
        return redirect(url_for('general'))
    
    record_page_visit(f'compare/{dish_name}')
    
    return render_template('compare.html', dish=dish, dishes=dishes)

# History route
@app.route('/history/<int:history_id>')
def history_page(history_id):
    regions, dishes, quiz, history = load_data()
    
    if history_id <= 0 or history_id > len(history):
        return redirect(url_for('general'))
    
    history_item = history[history_id - 1]
    record_page_visit(f'history/{history_id}')
    
    next_history = history_id + 1 if history_id < len(history) else None
    
    return render_template('history.html', 
                          history_item=history_item, 
                          history_id=history_id, 
                          next_history=next_history)

# Quiz routes
@app.route('/quiz')
def quiz_start():
    record_page_visit('quiz_start')
    return render_template('quiz_start.html')

@app.route('/quiz/<int:question_id>', methods=['GET', 'POST'])
def quiz(question_id):
    regions, dishes, quiz_data, history = load_data()
    
    if question_id <= 0 or question_id > len(quiz_data):
        return redirect(url_for('quiz_start'))
    
    user_data = init_user()
    
    # Handle POST request (answer submission)
    if request.method == 'POST':
        answer = request.form.get('answer')
        correct = answer == quiz_data[question_id - 1]['correct_answer']
        
        # Record the answer
        user_data['quiz_answers'].append({
            'question_id': question_id,
            'answer': answer,
            'correct': correct,
            'time': datetime.datetime.now().isoformat()
        })
        
        if correct:
            user_data['score'] += 1
        
        session['user_data'] = user_data
        
        # Redirect to next question or results
        if question_id < len(quiz_data):
            return redirect(url_for('quiz', question_id=question_id + 1))
        else:
            return redirect(url_for('quiz_results'))
    
    # GET request
    question = quiz_data[question_id - 1]
    record_page_visit(f'quiz/{question_id}')
    
    return render_template('quiz.html', 
                         question=question, 
                         question_id=question_id, 
                         total_questions=len(quiz_data))

@app.route('/quiz/results')
def quiz_results():
    user_data = init_user()
    record_page_visit('quiz_results')
    
    # Calculate score if not already done
    if 'score' not in user_data:
        user_data['score'] = sum(1 for answer in user_data['quiz_answers'] if answer['correct'])
        session['user_data'] = user_data
    
    regions, dishes, quiz_data, history = load_data()
    
    return render_template('quiz_results.html', 
                         user_data=user_data, 
                         total_questions=len(quiz_data))

# Save user data to JSON file (in real app, this would go to a database)
@app.route('/save_user_data', methods=['POST'])
def save_user_data():
    user_data = init_user()
    
    # Add any additional data from form
    for key, value in request.form.items():
        user_data[key] = value
    
    # In a real app, save to database
    # For this prototype, we'll just print the data
    print("User data saved:", user_data)
    
    session['user_data'] = user_data
    
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)