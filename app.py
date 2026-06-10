import os
import base64
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

# Initialize Groq Client securely
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CATEGORIES = [
    "Food & Dining", "Transport", "Shopping", "Utilities",
    "Healthcare", "Entertainment", "Travel", "Office Supplies", "Other"
]

expenses = []  # In-memory store

@app.route('/')
def index():
    return render_template('index.html', categories=CATEGORIES, expenses=expenses)

@app.route('/upload', methods=['POST'])
def upload_receipt():
    if 'receipt' not in request.files and 'text' not in request.form:
        return jsonify({'error': 'No input provided'}), 400

    image_data = None
    media_type = None

    if 'receipt' in request.files:
        file = request.files['receipt']
        if file.filename:
            content = file.read()
            image_data = base64.standard_b64encode(content).decode('utf-8')
            media_type = file.content_type or 'image/jpeg'

    text_input = request.form.get('text', '')

    groq_messages_content = []

    prompt = f"""Analyze this receipt/expense and extract details. Return ONLY a JSON object with these fields:
{{
  "merchant": "store or vendor name",
  "amount": 0.00,
  "currency": "USD",
  "date": "YYYY-MM-DD or empty string",
  "category": "one of: {', '.join(CATEGORIES)}",
  "items": ["list", "of", "items"],
  "notes": "brief summary"
}}

{"Receipt text instruction: " + text_input if text_input else "Analyze the receipt image provided."}

Return ONLY the JSON, no conversational filler, no markdown wrapping."""

    groq_messages_content.append({"type": "text", "text": prompt})

    if image_data:
        groq_messages_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{media_type};base64,{image_data}"
            }
        })

    try:
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[{"role": "user", "content": groq_messages_content}]
        )

        raw = response.choices[0].message.content.strip()
        
        if raw.startswith("```"):
            parts = raw.split("```")
            if len(parts) > 1:
                raw = parts[1]
                if raw.startswith("json"):
                    raw = raw[4:]
        raw = raw.strip()

        expense = json.loads(raw)
        expense['id'] = len(expenses) + 1
        expenses.append(expense)

        return jsonify({'success': True, 'expense': expense})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/expenses', methods=['GET'])
def get_expenses():
    category = request.args.get('category')
    filtered = expenses
    if category and category != 'All':
        filtered = [e for e in expenses if e.get('category') == category]
    total = sum(e.get('amount', 0) for e in filtered)
    return jsonify({'expenses': filtered, 'total': round(total, 2)})

@app.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    global expenses
    expenses = [e for e in expenses if e.get('id') != expense_id]
    return jsonify({'success': True})

@app.route('/summary', methods=['GET'])
def summary():
    by_category = {}
    for e in expenses:
        cat = e.get('category', 'Other')
        by_category[cat] = round(by_category.get(cat, 0) + e.get('amount', 0), 2)
    return jsonify({'by_category': by_category, 'total': round(sum(by_category.values()), 2)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)