from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from sqlalchemy import or_, asc, desc, func  # Added func for case-insensitive sorting

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a random string in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

# Define the Item model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=0)

# Define the form for adding items
class ItemForm(FlaskForm):
    sku = StringField('SKU', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    quantity = IntegerField('Initial Quantity', default=0)
    submit = SubmitField('Add Item')

# Home page redirects to inventory
@app.route('/')
def home():
    return redirect(url_for('inventory'))

# Route to add a new item
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    form = ItemForm()
    success = False
    if form.validate_on_submit():
        initial_quantity = form.quantity.data if form.quantity.data is not None else 0
        item = Item(sku=form.sku.data, description=form.description.data, category=form.category.data, quantity=initial_quantity)
        db.session.add(item)
        db.session.commit()
        success = True
        form = ItemForm(formdata=None)  # Clear the form after submission
    return render_template('add_item.html', form=form, success=success)

# Route to view and search inventory (updated for case-insensitive sorting)
@app.route('/inventory', methods=['GET'])
def inventory():
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'id')
    sort_direction = request.args.get('sort_direction', 'asc')  # Default to ascending
    if search:
        items = Item.query.filter(or_(Item.description.like(f'%{search}%'), Item.category.like(f'%{search}%')))
    else:
        items = Item.query
    if sort_by in ['sku', 'description', 'category', 'quantity']:
        column = getattr(Item, sort_by)
        if sort_by in ['sku', 'description', 'category']:  # String columns
            order_func = desc(func.lower(column)) if sort_direction == 'desc' else asc(func.lower(column))
        else:  # Quantity (numeric)
            order_func = desc(column) if sort_direction == 'desc' else asc(column)
        items = items.order_by(order_func)
    items = items.all()
    return render_template('inventory.html', items=items, search=search, sort_by=sort_by, sort_direction=sort_direction)

# Route for quick +1/-1 adjustments from inventory page
@app.route('/quick_adjust/<int:item_id>', methods=['POST'])
def quick_adjust(item_id):
    item = Item.query.get_or_404(item_id)
    action = request.form.get('action')
    search = request.form.get('search', '')
    sort_by = request.form.get('sort_by', 'id')
    sort_direction = request.form.get('sort_direction', 'asc')
    if action == 'add':
        item.quantity += 1
    elif action == 'subtract':
        item.quantity = max(0, item.quantity - 1)
    db.session.commit()
    return redirect(url_for('inventory', search=search, sort_by=sort_by, sort_direction=sort_direction))

# Route to delete an item from inventory
@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    search = request.form.get('search', '')
    sort_by = request.form.get('sort_by', 'id')
    sort_direction = request.form.get('sort_direction', 'asc')
    return redirect(url_for('inventory', search=search, sort_by=sort_by, sort_direction=sort_direction))

# Route to adjust item quantity
@app.route('/adjust/<int:item_id>', methods=['GET', 'POST'])
def adjust_quantity(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        action = request.form['action']
        try:
            amount = int(request.form['amount'])
            if amount < 1:
                raise ValueError
        except (KeyError, ValueError):
            amount = 1  # Default to 1 if invalid
        if action == 'add':
            item.quantity += amount
        elif action == 'subtract':
            item.quantity = max(0, item.quantity - amount)
        db.session.commit()
        return redirect(url_for('inventory'))
    return render_template('adjust.html', item=item)

# Run the app and create the database
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)  # HTTP for now