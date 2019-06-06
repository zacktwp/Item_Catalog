from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ProductCatagory, Product
from flask import session as login_session
import random
import string
app = Flask(__name__)

engine = create_engine('sqlite:///Product.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Everything Store home page
@app.route('/EverythingStore/')
def home():
    catagories = session.query(ProductCatagory).all()
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

if __name__ == '__main__':

    app.secret_key = 'super_secret_key'
    app.debug = True
    threaded=True
    app.run(host='0.0.0.0', port=8000)
