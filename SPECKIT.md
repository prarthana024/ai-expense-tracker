# SpecKit — AI Expense Tracker
**Hackathon 2 | Theme: Open | 1-member team**

---

## 1. Problem Statement

Manually tracking expenses from physical or digital receipts is tedious and error-prone. People forget to log expenses, miscategorize them, or spend significant time entering data. There is no quick way to just "show a receipt and get it tracked."

---

## 2. Solution

**AI Expense Tracker** is a web application where users upload a receipt image or paste receipt text, and an AI model automatically extracts the merchant name, amount, date, and best-fit spending category — no manual data entry required.

---

## 3. Target Users

- Students and young professionals tracking personal spending
- Freelancers logging business expenses
- Anyone who hates manual bookkeeping

---

## 4. Core Features

| # | Feature | Priority |
|---|---------|----------|
| 1 | Upload receipt image (JPG/PNG) → AI extracts details | Must Have |
| 2 | Paste receipt text → AI categorizes | Must Have |
| 3 | View list of all expenses | Must Have |
| 4 | Filter expenses by category | Must Have |
| 5 | Summary dashboard with category bars | Must Have |
| 6 | Delete individual expense | Must Have |
| 7 | Persistent DB storage | Nice to Have |
| 8 | CSV export | Nice to Have |
| 9 | Monthly budget alerts | Nice to Have |

---

## 5. Tech Architecture

```
[User Browser]
     │
     ▼
[Flask Web App — app.py]
     │
     ├──► /upload  ──► [Claude API (claude-sonnet-4)]
     │                       │
     │              Returns JSON: merchant, amount,
     │              date, category, items, notes
     │
     ├──► /expenses  (list, filter, delete)
     └──► /summary   (category-wise totals)
```

**Stack:**
- Language: Python 3.10+
- Web Framework: Flask 3.x
- AI: Anthropic Claude API (`claude-sonnet-4-20250514`)
- Frontend: Vanilla HTML/CSS/JS (single template)
- Storage: In-memory list (session-scoped)

---

## 6. AI Integration Details

**Model used:** `claude-sonnet-4-20250514`

**Input to Claude:**
- Receipt image (base64-encoded, sent as vision input), or
- Receipt text (sent as plain text)

**Prompt strategy:**
- Instructs Claude to return ONLY a JSON object (no preamble)
- Specifies exact fields: `merchant`, `amount`, `currency`, `date`, `category`, `items`, `notes`
- Provides the category list to constrain classification output

**Output parsing:**
- Strips markdown code fences if present
- Parses with `json.loads()`
- Falls back to error response with HTTP 500 if parsing fails

---

## 7. API Endpoints

| Method | Route | Input | Output |
|--------|-------|-------|--------|
| GET | `/` | — | HTML page |
| POST | `/upload` | `multipart/form-data`: `receipt` (file) and/or `text` | `{success, expense}` JSON |
| GET | `/expenses?category=X` | Optional category filter | `{expenses[], total}` |
| DELETE | `/expenses/<id>` | Expense ID in URL | `{success}` |
| GET | `/summary` | — | `{by_category{}, total}` |

---

## 8. Data Model

```json
{
  "id": 1,
  "merchant": "Swiggy",
  "amount": 349.00,
  "currency": "₹",
  "date": "2025-06-09",
  "category": "Food & Dining",
  "items": ["Biryani", "Cold Drink"],
  "notes": "Lunch delivery from Swiggy"
}
```

---

## 9. Categories

Food & Dining · Transport · Shopping · Utilities · Healthcare · Entertainment · Travel · Office Supplies · Other

---

## 10. Setup Instructions

```bash
git clone <repo-url>
cd ai-expense-tracker
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python app.py
# Open http://localhost:5000
```

---

## 11. Limitations & Assumptions

- Storage is in-memory; data is lost on server restart (acceptable for hackathon scope)
- No user authentication (single-user, local use assumed)
- Currency defaults to ₹ if not detected in receipt
- Accuracy depends on receipt readability (blurry images may yield partial results)

---

## 12. Demo Flow

1. Open `http://localhost:5000`
2. Upload a receipt image (or paste text like: *"Domino's Pizza - 1 Medium Pizza ₹349, Garlic Bread ₹99. Total: ₹448"*)
3. Click **Analyze with AI**
4. See extracted merchant, amount, and category appear instantly
5. View updated expense list and category summary bars
6. Filter by category or delete any entry

---

*Submitted for Hackathon 2 — GitLab repo by 4:30 PM, SpecKit by 6:00 PM*
