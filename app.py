import os
import base64
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

# Replace your old client.messages.create with this:
response = client.chat.completions.create(
    model="llama-3.2-11b-vision-preview",  # Groq's excellent vision model
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this receipt and return the total amount and items as JSON."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}" # Assumes your code converts image to base64
                    }
                }
            ]
        }
    ]
)

# Update how you grab the text result:
result_text = response.choices[0].message.content

CATEGORIES = [
    "Food & Dining", "Transport", "Shopping", "Utilities",
    "Healthcare", "Entertainment", "Travel", "Office Supplies", "Other"
]

expenses = []  # In-memory store (replace with DB in production)

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

    # Build message to Claude
    user_content = []

    if image_data:
        user_content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": image_data}
        })

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

{"Receipt text: " + text_input if text_input else "Analyze the receipt image above."}

Return ONLY the JSON, no explanation."""

    user_content.append({"type": "text", "text": prompt})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": user_content}]
        )

        raw = response.content[0].text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
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

import os

if __name__ == "__main__":
    # Render provides a PORT environment variable. If not found, default to 5000.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)