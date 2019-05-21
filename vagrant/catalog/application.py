from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ProductCatagory, Product
app = Flask(__name__)

engine = create_engine('sqlite:///Product.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/ProductCatagory/<int:ProductCatagory_id>/')
def ProductCat(ProductCatagory_id):
    product_cat = session.query(ProductCatagory).filter_by(id=ProductCatagory_id).one()
    items = session.query(Product).filter_by(ProductCatagory_id=product_cat.id)
    return render_template('products.html', ProductCatagory=product_cat, items=items)


# Task 1: Creae route for newMenuItem function here

@app.route('/ProductCatagory/<int:ProductCatagory_id>/new/', methods=['GET', 'POST'])
def newProductItem(ProductCatagory_id):
    if request.method == 'POST':
        newItem = Product(
            name=request.form['name'], ProductCatagory_id=ProductCatagory_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('ProductCat', ProductCatagory_id=ProductCatagory_id))
    else:
        return render_template('newproductitem.html', ProductCatagory_id=ProductCatagory_id)

# Task 2: Create route for editMenuItem function here
'''
@app.route('/ProductCatagory/<int:ProductCatagory_id>/<int:Product_id>/edit/')
def editProductItem(ProductCatagory_id, Product_id):
    return "page to edit a menu item. Task 2 complete!"
'''
@app.route('/ProductCatagory/<int:ProductCatagory_id>/<int:Product_id>/edit',
           methods=['GET', 'POST'])
def editProductItem(ProductCatagory_id, Product_id):
    editedItem = session.query(Product).filter_by(id=Product_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('ProductCat', ProductCatagory_id=ProductCatagory_id))
    else:
        # USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU
        # SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
        return render_template(
            'editproductitem.html', ProductCatagory_id=ProductCatagory_id, Product_id=Product_id, item=editedItem)

# Task 3: Create a route for deleteMenuItem function here
'''
@app.route('/ProductCatagory/<int:ProductCatagory_id>/<int:Product_id>/delete/')
def deleteProductItem(ProductCatagory_id, Product_id):
    return "page to delete a menu item. Task 3 complete!"
'''
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
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
