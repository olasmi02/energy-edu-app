from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS
import google.generativeai as genai
import markdown
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# load environment variable 
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Configure Gemini API 
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/progress')
def progress():
    return render_template('progress.html')

@app.route('/ask', methods=['POST'])
def ask_gemini():
    question = request.json['question']
    prompt = f"Question about energy policies or transition technologies: {question}\nAnswer:"
    response = model.generate_content(prompt)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(response.text)
    
    return jsonify({'response': html_content})

@app.route('/generate-question', methods=['GET'])
def generate_question():
    prompt = """Generate a multiple-choice question about energy policies or transition technologies. 
    The response should be in the following JSON format:
    {
        "question": "The question text",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_index": 0  // Index of the correct answer (0-3)
    }"""
    
    response = model.generate_content(prompt)
    return jsonify(response.text)

@app.route('/check-answer', methods=['POST'])
def check_answer():
    data = request.json
    question = data['question']
    user_answer = data['user_answer']
    correct_answer = data['correct_answer']
    
    prompt = f"""Question: {question}
    User's answer: {user_answer}
    Correct answer: {correct_answer}
    
    Evaluate if the user's answer is correct. If it's not exactly correct, determine if it's partially correct or contains any valid points. 
    Provide a brief explanation of why the answer is correct, partially correct, or incorrect.
    The response should be in the following JSON format:
    {{
        "is_correct": true/false,
        "explanation": "Explanation text"
    }}"""
    
    response = model.generate_content(prompt)
    return jsonify(response.text)

@app.route('/get_progress')
def get_progress():
    # In a real application, this data would come from a database
    # For now, we'll use session data as a simple stand-in
    if 'progress' not in session:
        session['progress'] = {
            'topics_completed': [],
            'quiz_scores': {},
            'certificates': []
        }
    
    return jsonify(session['progress'])

@app.route('/update_progress', methods=['POST'])
def update_progress():
    data = request.json
    if 'progress' not in session:
        session['progress'] = {
            'topics_completed': [],
            'quiz_scores': {},
            'certificates': []
        }
    
    if 'topic' in data:
        if data['topic'] not in session['progress']['topics_completed']:
            session['progress']['topics_completed'].append(data['topic'])
    
    if 'quiz' in data and 'score' in data:
        session['progress']['quiz_scores'][data['quiz']] = data['score']
    
    if 'certificate' in data:
        session['progress']['certificates'].append({
            'name': data['certificate'],
            'date': datetime.now().strftime("%B %d, %Y")
        })
    
    session.modified = True
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)