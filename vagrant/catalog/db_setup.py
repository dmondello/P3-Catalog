import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# Create a new declarative_base for our database model
Base = declarative_base()


# Create table for users
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(80), nullable=False, default='no_image.jpg')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.role,
            'picture': self.surname,
        }


# Create table for teams
class Team(Base):
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    logo = Column(String(80), nullable=False, default='no_logo.png')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'logo': self.logo,
        }


# Create Table for Players
class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    picture = Column(String(80), nullable=False, default='no_image.jpg')
    name = Column(String(80), nullable=False)
    surname = Column(String(80), nullable=False)
    role = Column(String(50))
    team_id = Column(Integer, ForeignKey('team.id'))
    team = relationship(Team)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'surname': self.surname,
            'role': self.role,
            'id': self.id,
        }


engine = create_engine('sqlite:///teams.db')

Base.metadata.create_all(engine)
