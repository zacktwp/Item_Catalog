import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class ProductCatagory(Base):
    __tablename__ = 'ProductCatagory'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
    	return{'name': self.name, 'id': self.id, }


class Product(Base):
    __tablename__ = 'Product'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    ProductCatagory_id = Column(Integer,
                                ForeignKey('ProductCatagory.id'))
    ProductCatagory = relationship(ProductCatagory)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        return{'name': self.name, 'description': self.description,
               'id': self.id, 'price': self.price,
               }


engine = create_engine('sqlite:///Product.db')


Base.metadata.create_all(engine)
