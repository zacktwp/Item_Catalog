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

@app.route('/ProductCatagory/<int:ProductCatagory_id>/product/JSON')
def ProductCatJSON(ProductCatagory_id):
    product_cat = session.query(ProductCatagory).filter_by(id=ProductCatagory_id).one()
    items = session.query(Product).filter_by(
        ProductCatagory_id=ProductCatagory_id).all()
    return jsonify(Product=[i.serialize for i in items])

@app.route('/')
@app.route('/ProductCatagory/<int:ProductCatagory_id>/')
#@app.route('/EverythingStore/')
def ProductCat(ProductCatagory_id):
    productcatagory = session.query(ProductCatagory).filter_by(id=ProductCatagory_id).one()
    items = session.query(Product).filter_by(ProductCatagory_id=ProductCatagory_id)
    catagories = session.query(ProductCatagory).all()
    return render_template(
        'products.html', productcatagory=productcatagory, ProductCatagory_id=ProductCatagory_id, items=items, catagories=catagories)


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html')


@app.route('/EverythingStore/')
def home():
    catagories = session.query(ProductCatagory).all()
    return render_template(
        'home.html', catagories=catagories)

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

@app.route('/EverythingStore/new/', methods=['GET', 'POST'])
def newProductItem():
    if request.method == 'POST':
        newItem = Product(name=request.form['name'])
        session.add(newItem)
        session.commit()
        flash("new menu item created!")
        return redirect(url_for('home'))
    else:
        return render_template('newproductitem.html')


# Task 1: Creae route for newMenuItem function here
'''
@app.route('/ProductCatagory/<int:ProductCatagory_id>/new/', methods=['GET', 'POST'])
def newProductItem(ProductCatagory_id):
    if request.method == 'POST':
        newItem = Product(
            name=request.form['name'], ProductCatagory_id=ProductCatagory_id)
        session.add(newItem)
        session.commit()
        flash("new menu item created!")
        return redirect(url_for('ProductCat', ProductCatagory_id=ProductCatagory_id))
    else:
        return render_template('newproductitem.html', ProductCatagory_id=ProductCatagory_id)
'''
# Task 2: Create route for editMenuItem function here

@app.route('/ProductCatagory/<int:ProductCatagory_id>/<int:Product_id>/edit',
           methods=['GET', 'POST'])
def editProductItem(ProductCatagory_id, Product_id):
    editedItem = session.query(Product).filter_by(id=Product_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('ProductCat', ProductCatagory_id=ProductCatagory_id))
    else:
        # USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU
        # SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
        return render_template(
            'editproductitem.html', ProductCatagory_id=ProductCatagory_id, Product_id=Product_id, item=editedItem)

# Task 3: Create a route for deleteMenuItem function here

@app.route('/ProductCatagory/<int:ProductCatagory_id>/<int:Product_id>/delete',
           methods=['GET', 'POST'])
def deleteProductItem(ProductCatagory_id, Product_id):
    itemToDelete = session.query(Product).filter_by(id=Product_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('ProductCat', ProductCatagory_id=ProductCatagory_id))
    else:
        return render_template('deleteproductitem.html', item=itemToDelete)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
