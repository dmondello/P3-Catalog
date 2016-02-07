from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Team, Base, Player,User

engine = create_engine('sqlite:///teams.db')
# Bind the engine to the metadata of the Base class so that the
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
session = DBSession()

# User John Wayne
user1 = User(name="John Wayne", email="johnwayne@western.com")
session.add(user1)
session.commit()


# Team Juventus
team1 = Team(name="Juventus", logo="juventus.png", user_id=1)
session.add(team1)
session.commit()

Player1 = Player(name="Roberto", surname="Baggio", role="Attack", team=team1, user_id=1)
session.add(Player1)
session.commit()

Player2 = Player(name="Claudio", surname="Gentile", role="Defense", team=team1, user_id=1)
session.add(Player2)
session.commit()

Player3 = Player(name="Umberto", surname="Conti", role="Defense", team=team1, user_id=1)
session.add(Player3)
session.commit()


# Team Milan
team2 = Team(name="Milan", logo="milan.png", user_id=1)
session.add(team2)
session.commit()

Player4 = Player(name="Riccardo", surname="Meda", role="Attack",  team=team2, user_id=1)
session.add(Player4)
session.commit()

Player5 = Player(name="Daniele", surname="Costo", role="Defense", team=team2, user_id=1)
session.add(Player5)
session.commit()

Player6 = Player(name="Franco", surname="Vasques", role="Defense",  team=team2, user_id=1)
session.add(Player6)
session.commit()


# Team Palermo
team3 = Team(name="Palermo", logo="palermo.png", user_id=1)

session.add(team3)
session.commit()

Player7 = Player(name="Fabrizio", surname="Sorrentino", role="Attack", team=team3, user_id=1)
session.add(Player7)
session.commit()

Player8 = Player(name="Daniele", surname="Costo", role="Defense", team=team3, user_id=1)
session.add(Player8)
session.commit()

Player9 = Player(name="Ugo", surname="Fantozzi", role="Defense", team=team3, user_id=1)
session.add(Player9)
session.commit()


# Team Partinico
team4 = Team(name="Partinico",user_id=1)

session.add(team4)
session.commit()

Player10 = Player(name="Ciccio", surname="Pasticcio", role="Attack", team=team4, user_id=1)
session.add(Player10)
session.commit()

Player11 = Player(name="Dany", surname="Boom", role="Defense", team=team4, user_id=1)
session.add(Player11)
session.commit()

Player12 = Player(name="Jhonny", surname="walker", role="Defense", team=team4, user_id=1)
session.add(Player12)
session.commit()

print "Added Teams an Players!"
