import sqlite3
from flask import Flask, render_template, request, redirect, session, flash, url_for
from google import genai
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = "snapspend_secret_key_12345"

# Ensure database tables exist on startup
def init_db():
    conn = sqlite3.connect("snapspend.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
                   amount REAL,
                   category TEXT,
                   description TEXT,
                   date TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budget(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monthly_budget REAL
)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS goals(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_name TEXT,
    target_amount REAL
)
""")
    conn.commit()
    conn.close()

init_db()

# Decorator to secure routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/add")
@login_required
def add_expense():
    return render_template("add_expense.html")
@app.route("/expenses")
@login_required
def expenses():
    selected_date = request.args.get("to_date")
    search=request.args.get("search")
    month=request.args.get("month")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    conn=sqlite3.connect("snapspend.db")
    cursor=conn.cursor()
    if from_date and to_date:
        cursor.execute("SELECT * FROM expenses WHERE category LIKE ?", ('%'+search+'%',))
        row=cursor.fetchall()
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE category LIKE ?", ('%'+search+'%',))
        total = cursor.fetchone()[0] or 0
    else:
        cursor.execute("SELECT id,amount,category, date FROM expenses")
        row=cursor.fetchall()
        cursor.execute("SELECT SUM(amount) FROM expenses")
        total = cursor.fetchone()[0] or 0
        month = request.args.get("month")
        conn=sqlite3.connect("snapspend.db")
        cursor=conn.cursor()
        if month:
            cursor.execute("""
                           SELECT * FROM expenses
                           WHERE substr(date,4,2)=?
                           AND substr(date,7,4)=?
                           """, (month))
            row=cursor.fetchall()
            cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE substr(date,1,7)=?
        """, (month,))
            total = cursor.fetchone()[0] or 0
        elif search:
            cursor.execute(
            "SELECT * FROM expenses WHERE category LIKE ?",
            ('%' + search + '%',)
        )
            row = cursor.fetchall()
            cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE category LIKE ?",
            ('%' + search + '%',)
        )
            total = cursor.fetchone()[0] or 0
        else:
            cursor.execute("SELECT * FROM expenses")
            row=cursor.fetchall()
            cursor.execute("SELECT SUM(amount) FROM expenses")
            total = cursor.fetchone()[0] or 0
            print(cursor.fetchall())
            cursor.execute("SELECT date FROM expenses")
            print(cursor.fetchall())
            cursor.execute("SELECT * FROM expenses")
            print(cursor.fetchall())
            print("Rows:", row)
            print("Month:", month)
            if selected_date:
                cursor.execute("""
                               SELECT * FROM expenses
                               WHERE date = ?
                               """, (selected_date,))
                row = cursor.fetchall()
                cursor.execute("""
                              SELECT SUM(amount)
                              FROM expenses
                              WHERE date = ?
                              """, (selected_date,))
                total = cursor.fetchone()[0] or 0
                conn.close()
    return render_template("expenses.html", row=row, total=total)
@app.route("/submit",methods=["POST"])
@login_required
def submit():
    amount=request.form["amount"]
    category=request.form["category"]
    description=request.form["description"]
    date=request.form["date"]
    print("Form received")
    print(amount, category, description, date)
    conn=sqlite3.connect("snapspend.db")
    cursor=conn.cursor()
    print("Saving:", amount, category, description, date)
    cursor.execute(
        "INSERT INTO expenses(amount,category,description,date) VALUES (?,?,?,?)",
        (amount,category,description,date)
)
    conn.commit()
    conn.close()
    return redirect("/expenses")
    return f"""
    Expense Submitted Succefully!<br>
    Amount:{amount}<br>
    Category:{category}<br>
    Description:{description}<br>
    Date:{date}
    """
    return "Expenses Submitted Successfully"
@app.route("/delete/<int:id>")
@login_required
def delete_expense(id):
    conn=sqlite3.connect("snapspend.db")
    cursor=conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?",
    (id,)
    )
    conn.commit()
    conn.close()
    return redirect("/expenses")
@app.route("/dashboard")
@login_required
def dashboard():
    conn=sqlite3.connect("snapspend.db")
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_expense=cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM expenses")
    count = cursor.fetchone()[0]
    cursor.execute("SELECT monthly_budget FROM budget LIMIT 1")
    budget_data = cursor.fetchone()
    monthly_budget = budget_data[0] if budget_data else 0
    
    # 1. Budget Alerts
    alert=""
    if monthly_budget > 0:
        percentage = (total_expense / monthly_budget) * 100
        if percentage >= 100:
            alert = "🚨 Budget Exceeded!"
        elif percentage >= 80:
            alert = "⚠️ Warning! You have used 80% of your budget."
            
    # 2. Category Aggregations
    cursor.execute("""
                   SELECT category, SUM(amount) 
                   FROM expenses
                   GROUP BY category
                   """)
    categories = cursor.fetchall()
    labels=[]
    amounts=[]
    for category in categories:
        labels.append(category[0])
        amounts.append(category[1])
        
    category_percentages=[]
    for category,amount in categories:
        if total_expense > 0:
            percentage = round((amount / total_expense) * 100, 1)
        else:
            percentage=0
        category_percentages.append({
            "category": category,
            "amount": amount,
            "percentage": percentage  
        }) 
        
    top_category = max(
        category_percentages,
        key=lambda x: x["amount"]
    ) if category_percentages else None
    
    current_savings = monthly_budget - total_expense
    
    # 3. Savings Goal
    cursor.execute("SELECT goal_name, target_amount FROM goals LIMIT 1")
    goal_data = cursor.fetchone()
    goal_name = ""
    target_amount = 0
    goal_progress = 0
    if goal_data:
        goal_name = goal_data[0]
        target_amount = goal_data[1]
        if target_amount > 0:
            goal_progress = round((current_savings / target_amount) * 100, 1)
        if goal_progress > 100:
            goal_progress = 100
        elif goal_progress < 0:
            goal_progress = 0
            
    # 4. Expense Trend (Python Parser for mixed date formats)
    cursor.execute("SELECT amount, date FROM expenses")
    all_expenses = cursor.fetchall()
    
    monthly_data = {}
    day_data = {"Monday": 0.0, "Tuesday": 0.0, "Wednesday": 0.0, "Thursday": 0.0, "Friday": 0.0, "Saturday": 0.0, "Sunday": 0.0}
    
    for amount, date_str in all_expenses:
        if not date_str:
            continue
        parsed_date = None
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'):
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                break
            except ValueError:
                continue
        
        if parsed_date:
            # Monthly trend
            month_key = parsed_date.strftime('%Y-%m') # e.g. "2026-06"
            monthly_data[month_key] = monthly_data.get(month_key, 0.0) + (amount or 0.0)
            # Day of week trend
            day_name = parsed_date.strftime('%A')
            day_data[day_name] = day_data.get(day_name, 0.0) + (amount or 0.0)
            
    # Sorted months for trend chart
    sorted_months = sorted(monthly_data.keys())
    trend_labels = []
    trend_amounts = []
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    for month_key in sorted_months:
        year, month = month_key.split('-')
        month_idx = int(month) - 1
        month_name = month_names[month_idx]
        trend_labels.append(f"{month_name} '{year[2:]}")
        trend_amounts.append(round(monthly_data[month_key], 2))
        
    # Sorted day-of-week lists
    weekday_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday_amounts = [
        round(day_data["Monday"], 2),
        round(day_data["Tuesday"], 2),
        round(day_data["Wednesday"], 2),
        round(day_data["Thursday"], 2),
        round(day_data["Friday"], 2),
        round(day_data["Saturday"], 2),
        round(day_data["Sunday"], 2)
    ]
    
    # Calculate Day-of-Week Insight
    weekday_sum = sum(day_data[d] for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    weekend_sum = sum(day_data[d] for d in ["Saturday", "Sunday"])
    
    day_insight = ""
    if weekday_sum > 0 or weekend_sum > 0:
        weekday_avg = weekday_sum / 5.0
        weekend_avg = weekend_sum / 2.0
        if weekend_avg > weekday_avg:
            day_insight = "💡 You spend the most on weekends."
        else:
            peak_day = max(day_data, key=day_data.get)
            day_insight = f"💡 You spend the most on weekdays (Peak day: {peak_day})."
        
    # 5. Month-over-Month Comparisons
    current_month_str = datetime.now().strftime('%Y-%m')
    current_total = monthly_data.get(current_month_str, 0.0)
    
    current_year_val = datetime.now().year
    current_month_val = datetime.now().month
    if current_month_val == 1:
        prev_month_str = f"{current_year_val - 1}-12"
    else:
        prev_month_str = f"{current_year_val}-{current_month_val - 1:02d}"
        
    previous_total = monthly_data.get(prev_month_str, 0.0)
    
    comparison_alert = ""
    if current_total > previous_total:
        difference = current_total - previous_total
        if previous_total > 0:
            pct = (difference / previous_total) * 100
            comparison_alert = f"⚠ You spent ₹{difference:.2f} ({pct:.1f}%) more than last month."
        else:
            comparison_alert = f"⚠ You spent ₹{difference:.2f} more than last month (no spending was recorded in the previous month)."
            
    conn.close()
    
    return render_template(
        "dashboard.html",
        total=total_expense,
        count=count,
        categories=categories,
        labels=labels,
        amounts=amounts,
        expenses=expenses,
        total_expense=total_expense,
        monthly_budget=monthly_budget,
        alert=alert,
        category_percentages=category_percentages,
        top_category=top_category,
        goal_name=goal_name,
        target_amount=target_amount,
        current_savings=current_savings,
        goal_progress=goal_progress,
        comparison_alert=comparison_alert,
        trend_labels=trend_labels,
        trend_amounts=trend_amounts,
        weekday_labels=weekday_labels,
        weekday_amounts=weekday_amounts,
        day_insight=day_insight
    )
@app.route("/upload")
@login_required
def upload_page():
    return render_template("upload.html")
@app.route("/upload", methods=["POST"])
@login_required
def upload_receipt():
    client=genai.Client(api_key="AQ.Ab8RN6LqjsDjjwul0Zdre5cy4fcW2VLI6Aurt78D6bhsHoNu1w")
    file = request.files["receipt"]
    allowed_extensions = (".jpg", ".jpeg", ".png")
    if not file.filename.lower().endswith(allowed_extensions):
        return "Please upload only JPG, JPEG, or PNG receipt images."
    filepath="uploads/"+file.filename
    print("File saved:", filepath)
    file.save(filepath)
    print("File saved:", filepath)
    try:
        print("Uploading to Gemini...")
        uploaded_file=client.files.upload(file=filepath)
        print("Upload successful")
        response=client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            """
            If this is not a receipt or bill, reply exactly:
            NOT_A_RECEIPT
            Otherwise return:
            {
            Store Name:
            Date:
            Total Amount:
            Category:
            }
            Choose the category from:
            Food, Grocery, Travel, Shopping,
            Medical, Entertainment, Utilities, Other
            """,
            uploaded_file
            ]
            )
        print(response.text)
        
        # Parse response text (JSON or NOT_A_RECEIPT)
        import json
        import re
        
        clean_text = response.text.strip()
        if clean_text.startswith("```"):
            clean_text = re.sub(r'^```(?:json)?\n', '', clean_text)
            clean_text = re.sub(r'\n```$', '', clean_text)
            clean_text = clean_text.strip()
            
        if clean_text == "NOT_A_RECEIPT":
            flash("The uploaded image does not appear to be a receipt.", "error")
            return redirect("/upload")
            
        try:
            data = json.loads(clean_text)
            store_name = data.get("Store Name", "Unknown Store")
            date = data.get("Date", "")
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            amount_str = data.get("Total Amount", "0.0")
            amount_clean = re.sub(r'[^\d.]', '', str(amount_str))
            amount = float(amount_clean) if amount_clean else 0.0
            category = data.get("Category", "Other")
        except Exception as e:
            print("Error parsing Gemini JSON:", e)
            store_name = "Unknown Store"
            date = datetime.now().strftime("%Y-%m-%d")
            amount = 0.0
            category = "Other"

        conn = sqlite3.connect("snapspend.db")
        cursor = conn.cursor()
        cursor.execute(
             "INSERT INTO expenses(amount, category, description, date) VALUES (?, ?, ?, ?)",
             (amount, category, store_name, date)
             )
        conn.commit()
        conn.close()
        flash("Receipt scanned and logged successfully!", "success")
        return redirect("/expenses")
    except Exception as e:
        flash(f"Gemini Error: {e}", "error")
        return redirect("/upload")
@app.route("/edit/<int:id>")
@login_required
def edit_expense(id):
    conn=sqlite3.connect("snapspend.db")
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id=?",(id,))
    expense=cursor.fetchone()
    conn.close()
    return render_template("edit_expense.html",expense=expense)
@app.route("/update/<int:id>", methods=["POST"])
@login_required
def update_expense(id):

    amount = request.form["amount"]
    category = request.form["category"]
    description = request.form["description"]
    date = request.form["date"]

    conn = sqlite3.connect("snapspend.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE expenses
        SET amount=?, category=?, description=?, date=?
        WHERE id=?
        """,
        (amount, category, description, date, id)
    )

    conn.commit()
    conn.close()
    return redirect("/expenses")
@app.route("/chat")
@login_required
def chat():
    return render_template("chat.html")  
@app.route("/ask",methods=["POST"])
@login_required
def ask():
    question=request.form["question"]
    conn=sqlite3.connect("snapspend.db")
    cursor=conn.cursor()
    cursor.execute("SELECT category,amount,date FROM expenses")
    expenses=cursor.fetchall()
    conn.close()
    prompt = f"""
    Expenses:
    {expenses}

    Answer using ONLY the expense data above.

    Question:
    {question}
    """
    client=genai.Client(api_key="AQ.Ab8RN6LqjsDjjwul0Zdre5cy4fcW2VLI6Aurt78D6bhsHoNu1w")
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text
    print(prompt)
    return prompt
    print(question)
    print(expenses)
    return "Data fetches successfully"
    return f"You asked:{question}"
@app.route("/register", methods=["GET", "POST"])
def register_page():
    if "user_id" in session:
        return redirect("/")
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")
            
        conn = sqlite3.connect("snapspend.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            flash("An account with that email already exists.", "error")
            return render_template("register.html")
            
        hashed_password = generate_password_hash(password)
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )
            conn.commit()
            conn.close()
            flash("Registration successful! Please log in.", "success")
            return redirect("/login")
        except Exception as e:
            conn.close()
            flash(f"Error during registration: {e}", "error")
            return render_template("register.html")
            
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if "user_id" in session:
        return redirect("/")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not email or not password:
            flash("All fields are required.", "error")
            return render_template("login.html")
            
        conn = sqlite3.connect("snapspend.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["user_email"] = user[2]
            flash(f"Welcome back, {user[1]}!", "success")
            return redirect("/")
        else:
            flash("Invalid email or password.", "error")
            return render_template("login.html")
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect("/")
@app.route('/set_budget', methods=['GET', 'POST'])
def set_budget():
    if request.method == 'POST':
        budget = request.form['budget']

        conn = sqlite3.connect('snapspend.db')
        c = conn.cursor()

        c.execute("DELETE FROM budget")
        c.execute(
            "INSERT INTO budget (monthly_budget) VALUES (?)",
            (budget,)
        )

        conn.commit()
        conn.close()

        flash("Budget Saved Successfully!")
        return redirect(url_for('dashboard'))

    return render_template('set_budget.html')

    conn.commit()
    conn.close()
@app.route("/set_goal",methods=["GET","POST"])
@login_required
def set_goal():
    if request.method=="POST":
        goal_name=request.form["goal_name"]
        target_amount=request.form["target_amount"]
        conn=sqlite3.connect("snapspend.db")
        cursor=conn.cursor()
        cursor.execute("DELETE FROM goals")

        cursor.execute(
            "INSERT INTO goals(goal_name, target_amount) VALUES(?,?)",
            (goal_name, target_amount)
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("set_goal.html")
                               
if __name__ == "__main__":
    print("Starting Flask")
    app.run(debug=True)