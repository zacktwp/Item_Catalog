from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ProductCatagory, Product

engine = create_engine('sqlite:///Product.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Below written queries have to be run by copping them into the git bash
# Query first Category name
first = session.query(ProductCatagory).first()
first.name
# u'Rice Dishes'

# Query all the Dishes in the database
ProductCatagory_id = 'Cleaning'
items = session.query(ProductCatagory).all()
for item in items:
	print (item.name)
