from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ProductCatagory, Product
from flask import session as login_session
import random
import string
app = Flask(__name__)

engine = create_engine('sqlite:///Product.db', pool_pre_ping=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Everything Store home page
@app.route('/EverythingStore/')
def home():
    catagories = session.query(ProductCatagory).all()
    items = session.query(Product).all()
    return render_template('home.html', catagories=catagories)

@app.route('/EverythingStore/<category_name>/items')
def allCategory(category_name):
    categories = session.query(ProductCatagory).order_by(asc(ProductCatagory.name))
    selectedCategory = session.query(ProductCatagory).filter_by(name=category_name).one()
    items = session.query(Product).filter_by(ProductCatagory_id=selectedCategory.id).order_by(asc(Product.name))
    return render_template('home.html', categories=categories, selectedCategory=selectedCategory, items=items)

@app.route('/EverythingStore/<category_name>/<item_name>')
def ProdDesc(category_name, item_name):
    category = session.query(ProductCatagory).filter_by(name=category_name).one()
    item = session.query(Product).filter_by(name=item_name, ProductCatagory=category).one()
    return render_template('description.html', item=item)

# Add new category
@app.route('/EverythingStore/newcategory', methods=['GET','POST'])
def addCategory():
    if request.method == 'POST':
        newCategory = ProductCatagory(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        flash("You've successfully added new category!")
        return redirect(url_for('home'))
    else:
        return render_template('newCategory.html', )

# Add new item to a category
@app.route('/EverythingStore/additem', methods=['GET','POST'])
def addItem():
    categories = session.query(ProductCatagory).all()
    if request.method == 'POST':
        itemName = request.form['name']
        itemDescription = request.form['description']
        itemCategory = session.query(ProductCatagory).filter_by(name=request.form['ProductCatagory']).one()
        if itemName != '':
            print("item name %s" % itemName)
            addingItem = Product(name=itemName, description=itemDescription, ProductCatagory=itemCategory)
            session.add(addingItem)
            session.commit()
            return redirect(url_for('home'))
        else:
            return render_template('addItem.html', categories=categories)
    else:
        return render_template('addItem.html', categories=categories)

# Edit  item to a category
@app.route('/EverythingStore/<category_name>/<item_name>/edit', methods=['GET','POST'])
def editItem(category_name, item_name):
    categories = session.query(ProductCatagory)
    editingItemCategory = session.query(ProductCatagory).filter_by(name=category_name).one()
    editingItem = session.query(Product).filter_by(name=item_name, ProductCatagory=editingItemCategory).one()
    if request.method == 'POST':
        if request.form['name']:
            editingItem.name = request.form['name']
        if request.form['description']:
            editingItem.description = request.form['description']
        if request.form['ProductCatagory']:
            editingItem.category = session.query(ProductCatagory).filter_by(name=request.form['ProductCatagory']).one()
        session.add(editingItem)
        session.commit()
        return redirect(url_for('ProdDesc', category_name=editingItemCategory.name, item_name=editingItem.name))
    else:
        return render_template('editItem.html', categories=categories, editingItemCategory=editingItemCategory, item=editingItem)

if __name__ == '__main__':

    app.secret_key = 'super_secret_key'
    app.debug = True
    threaded=True
    app.run(host='0.0.0.0', port=8000)
