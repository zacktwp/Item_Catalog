from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ProductCatagory, Product
app = Flask(__name__)

engine = create_engine('sqlite:///Product.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


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

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
