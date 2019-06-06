from flask import Flask, render_template, url_for, request, redirect, jsonify, make_response, flash
from flask import make_response
import json
from datetime import datetime

from werkzeug.utils import secure_filename
from werkzeug import url_decode
import requests

from database_setup import Base, ProductCatagory, Product
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2

app = Flask(__name__)

# Create session and connect to DB
engine = create_engine('sqlite:///Product.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Everything Store home page
@app.route('/catalog/')
def categories():
    categories = session.query(ProductCatagory).all()
    #items = session.query(Product)
    return render_template('catalog.html', categories=categories)

@app.route('/catalog/<category_name>/items')
def allCategoryItems(category_name):
    categories = session.query(ProductCatagory)
    selectedCategory = session.query(ProductCatagory).filter_by(name=category_name).one()
    items = session.query(Product).filter_by(category_id=selectedCategory.id)
    return render_template('catalog.html', categories=categories, selectedCategory=selectedCategory, items=items)

@app.route('/catalog/<category_name>/<item_name>')
def showItem(category_name, item_name):
  category = session.query(ProductCatagory).filter_by(name=category_name).one()
  item = session.query(Product).filter_by(name=item_name, ProductCatagory=category).one()
  return render_template('showItem.html', item=item)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
