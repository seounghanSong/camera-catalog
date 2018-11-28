from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'studio_user'

    id      = Column(Integer, primary_key=True)
    name    = Column(String(250), nullable=False)
    email   = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name'      : self.name,
            'id'        : self.id,
            'email'     : self.email,
            'picture'   : self.picture,
        }

class Company(Base):
    __tablename__ = 'company'

    id      = Column(Integer, primary_key=True)
    name    = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('studio_user.id'))
    user    = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name'      :self.name,
            'id'        :self.id,
        }

class Camera(Base):
    __tablename__ = 'camera'

    id          = Column(Integer, primary_key=True)
    name        = Column(String(250), nullable=False)
    description = Column(String(250))
    price       = Column(String(20))
    company_id  = Column(Integer, ForeignKey('company.id'))
    company     = relationship(Company)
    user_id     = user_id = Column(Integer, ForeignKey('studio_user.id'))
    user        = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name'          : self.name,
            'description'   : self.description,
            'id'            : self.id,
            'price'         : self.price,
        }

engine = create_engine('sqlite:///camerastudio.db')

Base.metadata.create_all(engine)
