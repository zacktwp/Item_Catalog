from flask import Flask
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
    prod = session.query(Product).filter_by(ProductCatagory_id=ProductCatagory.id)
    output = ''
    for i in prod:
        output += i.name
        output += '</br>'
        output += i.price
        output += '</br>'
        output += i.description
    return output

# Task 1: Create route for newMenuItem function here

@app.route('/ProductCatagory/<int:ProductCatagory_id>/new/')
def newProductItem(ProductCatagory_id):
    return "page to create a new menu item. Task 1 complete!"

# Task 2: Create route for editMenuItem function here

@app.route('/ProductCatagory/<int:ProductCatagory_id>/<int:Product_id>/edit/')
def editProductItem(ProductCatagory_id, Product_id):
    return "page to edit a menu item. Task 2 complete!"

# Task 3: Create a route for deleteMenuItem function here

@app.route('/ProductCatagory/<int:ProductCatagory_id>/<int:Product_id>/delete/')
def deleteProductItem(ProductCatagory_id, Product_id):
    return "page to delete a menu item. Task 3 complete!"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
