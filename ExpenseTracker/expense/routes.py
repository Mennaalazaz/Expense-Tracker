from expense import app, db
from expense import render_template
from expense import redirect, url_for, flash, request
from expense.forms import RegistrationForm, LoginForm, EditExpenseForm
from expense.models import User , Expense
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from collections import defaultdict


@app.route('/')
def home_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_page')) # if already logged in redirect to dashboard
    return render_template("home.html")  # else show home page


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegistrationForm()
    if form.validate_on_submit():
            # Check if user with same email, username, or password already exists
        if User.query.filter_by(email=form.email.data).first() or User.query.filter_by(username=form.username.data).first() or User.query.filter_by(password=form.password.data).first():
            flash('you already registered. Please log in.', 'danger')
            return redirect(url_for('login_page'))
        
        # Create a new user and add to the database
        user = User(username=form.username.data, email=form.email.data , password= form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user) # log in the user immediately after registration
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('dashboard_page'))
    
    # Display form errors if any
    if form.errors:
        for err_msg in form.errors.values():
            flash(f'Error: {err_msg}', 'danger')

    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if user exists and password is correct
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password_correction(form.password.data):
            login_user(user) # log in the user
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard_page'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    else:
        if form.errors:
            for err_msg in form.errors.values():
                flash(f'Error: {err_msg}', 'danger')        
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home_page'))


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard_page():
    # fetch all expenses for the logged-in user
    expenses = Expense.query.filter_by(user_id=current_user.id)
    # calculate some summary statistics
    # if no expenses, return 0 using "or 0"
    total_expense_this_month = Expense.query.filter_by(user_id=current_user.id).filter(db.extract('month', Expense.date) == datetime.now().month, db.extract('year', Expense.date) == datetime.now().year).with_entities(db.func.sum(Expense.amount)).scalar() or 0
    total_expense_this_year = Expense.query.filter_by(user_id=current_user.id).filter(db.extract('year', Expense.date) == datetime.now().year).with_entities(db.func.sum(Expense.amount)).scalar() or 0
    avg_daily_expense_amount = Expense.query.filter_by(user_id=current_user.id).filter(Expense.date == datetime.now().date()).with_entities(db.func.avg(Expense.amount)).scalar() or 0

    # executing the query to get all expenses as a list
    # .all returns a list of all results
    expenses = expenses.all

    # calculate the total expense grouped by category 
    category_totals = (
    db.session.query(Expense.category, db.func.sum(Expense.amount))
    .filter(Expense.user_id == current_user.id)
    .group_by(Expense.category)
    .all()
    )
    # unpack the results into two lists for charting
    categories = [row[0] for row in category_totals]
    category_values = [row[1] for row in category_totals]

    
    # calculate the total expense grouped by date
    date_totals = (
    db.session.query(Expense.date, db.func.sum(Expense.amount))
    .filter(Expense.user_id == current_user.id)
    .group_by(Expense.date)
    .order_by(Expense.date)  # ensures sorted by date
    .all()
    )
    dates = [row[0].strftime('%Y-%m-%d') for row in date_totals]  # format dates as strings
    date_values = [row[1] for row in date_totals]

    # Data for histogram (distribution of expense amounts)
    histogram_values = db.session.query(
        Expense.amount
    ).filter_by(user_id=current_user.id).all()
    # change the list of tuples to a flat list of floats
    histogram_values = [float(a[0]) for a in histogram_values]
    histogram_bins=[0, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]


    # Stacked bar chart data (Category by Month)
#     needed data must have this format 
#     data = {
#       labels: ["June", "July", "August"],
#       datasets: [
#       { label: "Food", data: [200, 150, 300], backgroundColor: "#ff6384" },
#       { label: "Transport", data: [100, 120, 90], backgroundColor: "#36a2eb" },
#        { label: "Bills", data: [250, 180, 220], backgroundColor: "#ffce56" }
#       ]
#    };

    # filter by month then category
    stacked_data = (
        db.session.query(
            db.extract('month', Expense.date).label('month'),
            Expense.category,
            db.func.sum(Expense.amount).label('total')
        )
        .filter(Expense.user_id == current_user.id)
        .group_by('month', Expense.category)
        .order_by('month')
        .all()
    )
    # this returns a list of tuples (month, category, total)
    # we need to transform this into a format suitable for charting
    # 1. Extract all months and categories from the query
    months = sorted({row[0] for row in stacked_data})      
    categories = sorted({row[1] for row in stacked_data})  

    # 2. Map category -> list of totals (default 0)
    category_totals = defaultdict(lambda: [0] * len(months))
         # defaultdict creates a dictionary where each key maps to a list of zeros, one for each month 
         # category_totals["Food"] = [0,0,0,...]
         #category_totals["Transport"] = [0,0,0,...] and so on for each category
    for month, category, total in stacked_data:
        category_totals[category][months.index(month)] = float(total)

    # 3. Build Chart.js datasets
    colors = ['#ff6384','#36a2eb','#ffce56','#4bc0c0','#9966ff','#ff9f40']
    datasets = [
        {"label": cat, "data": category_totals[cat], "backgroundColor": color}
        for cat, color in zip(categories, colors)
    ]
    
    # fetch last 5 expenses for the logged-in user
    recent_expenses = Expense.query.filter_by(user_id=current_user.id) \
                            .order_by(Expense.date.desc()) \
                            .limit(5).all()

    # render the dashboard template with all the data
    return render_template("dashboard.html", expenses=expenses,
                        total_expense_this_month=total_expense_this_month,
                        avg_expense_amount_this_year=total_expense_this_year,
                        avg_daily_expense_amount=avg_daily_expense_amount
                        , categories=categories, category_values=category_values
                        , dates=dates, date_values=date_values
                        , histogram_values=histogram_values, histogram_bins=histogram_bins
                        , stacked_labels=months, stacked_datasets=datasets
                        , recent_expenses=recent_expenses
                        )

@app.route('/editExpense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id) # get the expense or return 404 if not found
    form=EditExpenseForm(obj=expense)   # prefill the form with existing expense data
    if expense.user_id != current_user.id: # prevent editing others' expenses for security
        flash('You do not have permission to edit this expense.', 'danger')
        return redirect(url_for('dashboard_page'))

    if request.method == 'POST' and form.validate_on_submit(): # if form is submitted and valid
        expense.amount = float(request.form.get('amount'))
        expense.category = request.form.get('category')
        date_str = request.form.get('date')  
        expense.date= datetime.strptime(date_str, '%Y-%m-%d').date() # convert string to date object
        expense.description = request.form.get('description')
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('my_expenses_page'))
    return render_template("editExpense.html", expense=expense, form=form)

@app.route('/deleteExpense/<int:expense_id>', methods=['POST','GET'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        flash('You do not have permission to delete this expense.', 'danger')
        return redirect(url_for('dashboard_page'))
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('my_expenses_page'))


@app.route('/myExpenses', methods=['GET', 'POST'])
@login_required
def my_expenses_page():
    # Initial query to get all expenses for the current user
    query = Expense.query.filter_by(user_id=current_user.id)

    if request.method == 'POST':
        # Get filter criteria from the form
        date = request.form.get('date')
        category = request.form.get('category')
    
        # Apply filters if provided
        if date:
            query = query.filter(Expense.date == datetime.strptime(date, '%Y-%m-%d').date())
        if category:
            query = query.filter(Expense.category == category)  

        # Execute query
        expenses = query.all()    

    else: # GET request then Execute query without filters
        expenses = query.all()    
    return render_template("myExpenses.html", expenses=expenses)

@app.route('/addExpense', methods=['POST','GET'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        category = request.form.get('category')
        date_str = request.form.get('date')  # this gets the date string from the form
        date = datetime.strptime(date_str, '%Y-%m-%d').date() # convert string to date object
        description = request.form.get('description')

        
        new_expense = Expense(amount=amount, category=category, date=date, description=description, user_id=current_user.id)
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('my_expenses_page'))
    
    return render_template("addExpense.html") 