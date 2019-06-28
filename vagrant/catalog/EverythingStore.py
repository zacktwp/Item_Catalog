from flask import Flask, render_template
from flask import request, redirect, url_for, flash, jsonify
from datetime import datetime
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ProductCatagory, Product, User
from flask import session as login_session
import random
import string
from sqlalchemy import exc
from functools import wraps

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
        response = make_response(json.dumps('user is already connected.'),
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

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s'), access_token
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['user_id']
        del login_session['email']
        del login_session['picture']
        flash("You are now successfully logged out.")
        return redirect(url_for('home'))
    else:
        response = make_response(json.dumps('Failed to revoke token', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Adding primary routes.
def login_required(f):
    """Login decorater function."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/home')
        return f(*args, **kwargs)
    return decorated_function


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return newUser.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user.id


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Create anti-forgery state token
@app.route('/signin')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', state=state)


# API endpoint for Everyting Store
@app.route('/EverythingStore/json')
def EverythingStoreJSON():

    catagories = session.query(ProductCatagory).all()
    items = session.query(Product).all()
    return jsonify(Catagories=[c.serialize for c in catagories],
                   Items=[i.serialize for i in items])


# Everything Store home page
@app.route('/')
@app.route('/EverythingStore/')
def home():
    try:
        catagories = session.query(ProductCatagory).all()
        items = session.query(Product).all()
        user = login_session.get('username', None)
        return render_template('home.html', catagories=catagories, user=user)
    except exc.SQLAlchemyError:
        return '<h1>database error...re-try</h1>'


@app.route('/EverythingStore/<category_name>/items')
def allCategory(category_name):
    try:
        categories = session.query(
                                   ProductCatagory
                                   ).order_by(asc(ProductCatagory.name))
        selectedCat = session.query(
                                    ProductCatagory
                                    ).filter_by(name=category_name).one()
        items = session.query(
                              Product
                              ).filter_by(
                                          ProductCatagory_id=selectedCat.id
                                          ).order_by(asc(Product.name))
        return render_template('home.html', categories=categories,
                               selectedCategory=selectedCat, items=items)
    except exc.SQLAlchemyError:
        return '<h1>database error...re-try</h1>'


@app.route('/EverythingStore/<category_name>/<item_name>')
def ProdDesc(category_name, item_name):
    try:
        cat = session.query(
                            ProductCatagory
                            ).filter_by(name=category_name).one()
        item = session.query(
                             Product
                             ).filter_by(
                                         name=item_name, ProductCatagory=cat
                                         ).one()
        return render_template('description.html', item=item)
    except exc.SQLAlchemyError:
        return '<h1>database error...re-try</h1>'


# Add new category
@app.route('/EverythingStore/newcategory', methods=['GET', 'POST'])
@login_required
def addCategory():
    if request.method == 'POST':
        try:
            newCategory = ProductCatagory(name=request.form['name'])
            session.add(newCategory)
            session.commit()
            flash("You've successfully added new category!")
            return redirect(url_for('home'))
        except exc.SQLAlchemyError:
            return '<h1>database error...re-try</h1>'
    else:
        return render_template('newCategory.html', )


# Delete category
@app.route('/EverythingStore/<ProductCatagory_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteCatagory(ProductCatagory_id):
    categoryToDelete = session.query(
                                     ProductCatagory
                                     ).filter_by(name=ProductCatagory_id).one()
    # Delete category from the database
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        return redirect(url_for('home'))
    return render_template('deleteCatagory.html', category=categoryToDelete)


# Add new item to a category
@app.route('/EverythingStore/additem', methods=['GET', 'POST'])
@login_required
def addItem():
    categories = session.query(ProductCatagory).all()
    if request.method == 'POST':
        itemName = request.form['name']
        itemDescription = request.form['description']
        itCat = session.query(
                              ProductCatagory
                              ).filter_by(
                                          name=request.form['ProductCatagory']
                                          ).one()
        if itemName != '':
            print("item name %s" % itemName)
            addingItem = Product(name=itemName,
                                 description=itemDescription,
                                 ProductCatagory=itCat,
                                 user_id=login_session['user_id'])
            session.add(addingItem)
            session.commit()
            return redirect(url_for('home'))
        else:
            return render_template('addItem.html', categories=categories)
    else:
        return render_template('addItem.html', categories=categories)


# delete  item to a category
@app.route('/EverythingStore/<category_name>/<item_name>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteItem(category_name, item_name):
    deletingItemCategory = session.query(
                                        ProductCatagory
                                        ).filter_by(name=category_name).one()
    deletingItem = session.query(
                                 Product
                                 ).filter_by(name=item_name).one()
    creator = getUserInfo(deletingItem.user_id)
    if deletingItem.user_id != creator:
        return redirect('home')
    # Delete item from the database
    if request.method == 'POST':
        session.delete(deletingItem)
        session.commit()
        return redirect(url_for('home'))
    return render_template('deleteItem.html', item=deletingItem,
                           category_name=deletingItemCategory)


# Edit  item to a category
@app.route('/EverythingStore/<category_name>/<item_name>/edit',
           methods=['GET', 'POST'])
@login_required
def editItem(category_name, item_name):
    categories = session.query(ProductCatagory)
    editItCat = session.query(
                              ProductCatagory
                              ).filter_by(name=category_name).one()
    edIt = session.query(
                         Product
                         ).filter_by(
                                     name=item_name, ProductCatagory=editItCat
                                     ).one()
    creator = getUserInfo(edIt.user_id)
    if edIt.user_id != creator:
        return redirect('home')
    if request.method == 'POST':
        if request.form['name']:
            edIt.name = request.form['name']
        if request.form['description']:
            edIt.description = request.form['description']

        session.add(edIt)
        session.commit()
        return redirect(url_for('ProdDesc', category_name=editItCat.name,
                                item_name=edIt.name))
    else:
        return render_template('editItem.html', categories=categories,
                               editingItemCategory=editItCat, item=edIt)


if __name__ == '__main__':

    app.secret_key = 'super_secret_key'
    app.debug = True
    threaded = True
    app.run(host='0.0.0.0', port=8000)
