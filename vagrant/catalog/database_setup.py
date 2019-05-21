import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class ProductCatagory(Base):
    __tablename__ = 'ProductCatagory'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Product(Base):
    __tablename__ = 'Product'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    ProductCatagory_id = Column(Integer, ForeignKey('ProductCatagory.id'))
    ProductCatagory = relationship(ProductCatagory)


    @property
    def serialize(self):

        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
        }


engine = create_engine('sqlite:///Product.db')


Base.metadata.create_all(engine)
