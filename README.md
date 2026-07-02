# 💰 SnapSpend – AI-Powered Expense Tracker

SnapSpend is a web-based personal expense tracker built with **Python**, **Flask**, and **SQLite**. It helps users record, organize, and analyze their daily expenses through an intuitive interface. The application also includes **AI-powered receipt analysis** using the Google Gemini API to simplify expense entry.

---

## 📖 Overview

Managing daily expenses can be time-consuming, especially when entering data manually. SnapSpend streamlines this process by allowing users to record expenses, view spending history, analyze spending patterns, and use AI to extract information from receipts.

---

## ✨ Features

* 🔐 User Registration and Login
* 💵 Add, View, and Delete Expenses
* 📊 Dashboard with Expense Summary
* 📈 Category-wise Spending Analysis
* 🔍 Search Expenses by Category
* 🧾 AI Receipt Analysis using Google Gemini API
* 💾 SQLite Database for Data Storage
* 📱 Responsive User Interface

---

## 🛠️ Technologies Used

### Backend

* Python
* Flask

### Frontend

* HTML5
* CSS3
* JavaScript

### Database

* SQLite

### AI Integration

* Google Gemini API

---

## 📂 Project Structure

```text
snapspend/
│── app.py
│── create_db.py
│── gemini_test.py
│── snapspend.db
│── templates/
│── static/
└── README.md
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/snapspend.git
```

### 2. Navigate to the project

```bash
cd snapspend
```

### 3. Create a virtual environment (Optional)

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows**

```bash
.venv\Scripts\activate
```

**Linux/macOS**

```bash
source .venv/bin/activate
```

### 5. Install the required packages

```bash
pip install flask google-genai werkzeug
```

Or, if you have a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

### 7. Open the application

Visit:

```text
http://127.0.0.1:5000/
```

---

## 📸 Screenshots

Add screenshots of the following pages:

* Home Page
* Login Page
* Registration Page
* Add Expense
* Expense List
* Dashboard
* AI Receipt Analysis

---

## 🎯 Future Enhancements

* Monthly Budget Tracking
* Expense Editing
* Export Reports (PDF/Excel)
* Email Notifications
* OCR-based Receipt Scanning
* Expense Charts and Analytics
* Multi-user Support
* Cloud Database Integration

---

## 👩‍💻 Author

**Athira R**

MCA Graduate

Python | Flask | SQLite | Web Development

---

## 📄 License

This project is developed for educational and learning purposes.

---

## ⭐ Support

If you found this project helpful, please consider giving it a ⭐ on GitHub.
