import os
import random
import json
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "noor_learning_pro_99"

# পাসওয়ার্ড সেটআপ
CATEGORY_PASSWORDS = {
    'class1': '753',
    'class2': '951',
    'revision1': '741',
    'class3': '963',
    'revision2': '321',
    'class4': '745',
    'class5': '856',
    'revision3': '325',
    'class6': '658',
    'class7': '965',
    'revision4': '742',
    'superRevision1': '326',
    'class8': '853',
    'class9': '486',
    'revision5': '431',
    'superRevision2': '168',
    'ultraSuperRevision': '761',
}


def load_words_by_category(category):
    word_list = []
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, f"{category}.txt")
    if not os.path.exists(file_path): return None
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if ":" in line:
                parts = line.strip().split(":")
                if len(parts) == 2:
                    word_list.append({"en": parts[0].strip(), "bn": parts[1].strip()})
    return word_list


def save_to_leaderboard(name, score, category):
    file_path = 'leaderboard.json'
    data = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    data.append({'name': name, 'score': score, 'category': category})
    data = sorted(data, key=lambda x: x['score'], reverse=True)[:10]  # সেরা ১০ জন
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@app.route('/')
def Home():
    quizzes = [
        {'id': 'class1', 'name': 'প্রথম পাঠ', 'icon': '📚'},
        {'id': 'class2', 'name': 'দ্বিতীয় পাঠ', 'icon': '📚'},
        {'id': 'revision1', 'name': 'রিভিশন 1', 'icon': '📚'},
        {'id': 'class3', 'name': 'তৃতীয় পাঠ', 'icon': '📚'},
        {'id': 'revision2', 'name': 'রিভিশন 2', 'icon': '📚'},
        {'id': 'class4', 'name': 'চতুর্থ পাঠ', 'icon': '📚'},
        {'id': 'class5', 'name': 'পঞ্চম পাঠ', 'icon': '📚'},
        {'id': 'revision3', 'name': 'রিভিশন 3', 'icon': '📚'},
        {'id': 'class6', 'name': 'সষ্ঠ পাঠ', 'icon': '📚'},
        {'id': 'class7', 'name': 'সপ্তম পাঠ', 'icon': '📚'},
        {'id': 'revision4', 'name': 'রিভিশন 4', 'icon': '📚'},
        {'id': 'superRevision1', 'name': 'সুপার রিভিশন 1', 'icon': '📚'},
        {'id': 'class8', 'name': 'অষ্টম পাঠ', 'icon': '📚'},
        {'id': 'class9', 'name': 'নবম পাঠ', 'icon': '📚'},
        {'id': 'revision5', 'name': 'রিভিশন 5', 'icon': '📚'},
        {'id': 'superRevision2', 'name': 'সুপার রিভিশন 2', 'icon': '📚'},
        {'id': 'ultraSuperRevision', 'name': 'আল্ট্রা সুপার রিভিশন', 'icon': '📚'},
    ]
    return render_template('index.html', quizzes=quizzes)


@app.route('/quiz/<category>', methods=['GET', 'POST'])
def Quiz(category):
    if session.get(f'auth_{category}') != True:
        if request.method == 'POST' and 'quiz_password' in request.form:
            if request.form.get('quiz_password') == CATEGORY_PASSWORDS.get(category):
                session[f'auth_{category}'] = True
                return redirect(url_for('Quiz', category=category))
            return render_template('index.html', category=category, error="ভুল পাসওয়ার্ড!", show_pass=True)
        return render_template('index.html', category=category, show_pass=True)

    words = load_words_by_category(category)
    if not words: return "ফাইল পাওয়া যায়নি!"

    if 'current_category' not in session or session['current_category'] != category:
        session.update({'current_category': category, 'current_step': 0, 'score': 0})
        indices = list(range(len(words)))
        random.shuffle(indices)
        session['question_indices'] = indices
        session['modes'] = random.sample(['en_to_bn', 'bn_to_en'] * len(words), len(words))

    if session['current_step'] >= len(words):
        return redirect(url_for('Result'))

    if request.method == 'POST':
        if request.form.get('answer') == request.form.get('correct_answer'):
            session['score'] += 1
        session['current_step'] += 1
        return redirect(url_for('Quiz', category=category))

    step = session['current_step']
    word = words[session['question_indices'][step]]
    mode = session['modes'][step]

    question = f" {word['en']}     👉       অর্থ       👇 " if mode == 'en_to_bn' else f" {word['bn']}     👉       ইংরেজি       👇 "
    answer = word['bn'] if mode == 'en_to_bn' else word['en']

    options = random.sample([w['bn'] if mode == 'en_to_bn' else w['en'] for w in words if
                             (w['bn'] if mode == 'en_to_bn' else w['en']) != answer], min(len(words) - 1, 3)) + [answer]
    random.shuffle(options)

    return render_template('index.html', question=question, answer=answer, options=options, category=category,
                           step=step + 1)


@app.route('/result')
def Result():
    score = session.get('score', 0)
    total = len(session.get('question_indices', []))
    percent = (score / total) * 100 if total > 0 else 0
    color = "#28a745" if percent >= 80 else "#ffc107" if percent >= 50 else "#dc3545"
    return render_template('result.html', score=score, total=total, percentage=percent, color=color)


@app.route('/save_score', methods=['POST'])
def SaveScore():
    name = request.form.get('user_name')
    score = session.get('score', 0)
    category = session.get('current_category', 'General')
    save_to_leaderboard(name, score, category)
    session.clear()
    return redirect(url_for('Leaderboard'))


@app.route('/leaderboard')
def Leaderboard():
    scores = []
    if os.path.exists('leaderboard.json'):
        with open('leaderboard.json', 'r', encoding='utf-8') as f:
            scores = json.load(f)
    return render_template('leaderboard.html', scores=scores)


if __name__ == '__main__':
    app.run(debug=True)