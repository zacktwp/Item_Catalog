from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ProductCatagory, Product
from flask import session as login_session
import random
import string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Everything Store"

engine = create_engine('sqlite:///Product.db', pool_pre_ping=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# Create anti-forgery state token
@app.route('/signin')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

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

# Delete category
@app.route('/EverythingStore/<ProductCatagory_id>/delete',
           methods=['GET', 'POST'])
def deleteCatagory(ProductCatagory_id):

    categoryToDelete = session.query(ProductCatagory).filter_by(name=ProductCatagory_id).one()
    # Delete category from the database
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(url_for('home'))
    return render_template('deleteCatagory.html', category=categoryToDelete)

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
