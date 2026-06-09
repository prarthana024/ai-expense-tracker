# 🧾 AI Expense Tracker

An AI-powered expense tracker that automatically categorizes receipts from images or text using Claude AI.

## 🚀 Features

- 📸 **Upload receipt images** (JPG, PNG, etc.) and auto-extract merchant, amount, date, and items
- ✏️ **Paste receipt text** for instant AI categorization
- 🏷️ **Auto-categorizes** into 9 categories: Food & Dining, Transport, Shopping, Utilities, Healthcare, Entertainment, Travel, Office Supplies, Other
- 📊 **Visual summary** with category breakdown bars
- 🔍 **Filter expenses** by category
- 🗑️ **Delete** individual expenses
- ⚡ Built with **Flask + Claude AI (claude-sonnet-4)**

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10+, Flask |
| AI | Anthropic Claude API (claude-sonnet-4) |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Storage | In-memory (session-based) |

## ⚙️ Setup & Run

### 1. Clone the repo

```bash
git clone <your-gitlab-repo-url>
cd ai-expense-tracker
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your Anthropic API key

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

### 4. Run the app

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## 📁 Project Structure

```
ai-expense-tracker/
├── app.py              # Flask backend + Claude API integration
├── requirements.txt    # Python dependencies
├── uploads/            # Temp storage for uploaded images
└── templates/
    └── index.html      # Single-page frontend
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main web UI |
| POST | `/upload` | Upload receipt image or text for AI analysis |
| GET | `/expenses` | List all expenses (optional `?category=` filter) |
| DELETE | `/expenses/<id>` | Delete an expense |
| GET | `/summary` | Category-wise spending summary |

## 💡 How It Works

1. User uploads a receipt image or pastes receipt text
2. Flask sends the input to Claude AI with a structured prompt
3. Claude extracts: merchant name, amount, date, items, and best-fit category
4. The response is parsed as JSON and stored in memory
5. The UI updates with the new expense and refreshed summary

## 🏁 Hackathon Notes

- **Theme:** Open
- **Team size:** 1 member
- **Built in:** ~3 hours
- **Key AI capability used:** Claude's vision + structured JSON output

## 📌 Future Improvements

- PostgreSQL / SQLite persistent storage
- PDF receipt support
- Monthly budget alerts
- CSV export
- User authentication
