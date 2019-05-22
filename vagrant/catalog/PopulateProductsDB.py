from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import ProductCatagory, Base, Product

engine = create_engine('sqlite:///Product.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Products for Groceries
ProductCatagory1 = ProductCatagory(name="Groceries")

session.add(ProductCatagory1)
session.commit()

Product2 = Product(name="Tuna", description="Delicious Blue Finn Tuna, extra Dolphin",
                    price = "1.23", ProductCatagory=ProductCatagory1)
session.add(Product2)
session.commit()

print ("added products to DB!")
