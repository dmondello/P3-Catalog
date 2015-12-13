# Flask imports
import os
from flask import session as login_session
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask.ext.seasurf import SeaSurf
from flask import session as login_session

from werkzeug import secure_filename

# SQLAlchemy imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# For Upload file
UPLOAD_FOLDER = 'static/img/upload'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# Import content from database
from db_setup import Base, User, Team, Player

# Create Flask web application
app = Flask(__name__)

# SeaSurf, Flask extention to prevent cross-site request forgeries
csrf = SeaSurf(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create new database session using 'engine'
engine = create_engine('sqlite:///teams.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
@csrf.exempt
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

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = '<br><h3>'
    output += login_session['username']
    output += '<br></h3><img src="'
    output += login_session['picture']
    output += ' " style = "width: 50px; height: 50px;border-radius: ' \
              '50px;-webkit-border-radius: 50px;-moz-border-radius: 50px;"> '

    print "done!"
    return output


# User Helper Functions


# Create login session
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


#  Get User info
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


#  get User email
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        return redirect('/login')
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400
                       ))
        response.headers['Content-Type'] = 'application/json'
        return response


# Define the routes

# root of application
@app.route('/')
def showMenu():
    teams = session.query(Team).all()
    if 'username' not in login_session:
        return render_template('login.html', teams=teams)
    else:
        return render_template('teams.html', teams=teams)


# route to teams (public or private)
@app.route('/teams')
def showTeams():
    teams = session.query(Team).all()
    if 'username' not in login_session:
        return render_template('publicteams.html', teams=teams)
    else:
        return render_template('teams.html', teams=teams)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# route to add new team
@app.route('/team/new/', methods=['GET', 'POST'])
def newTeam():
    if'username' not in login_session:
        return redirect('/login')
    # If the value is in POST (User answered) insert the value
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        newTeam = Team(name=request.form['name'], logo=filename, user_id=login_session['user_id'])
        session.add(newTeam)
        session.commit()
        return redirect(url_for('showTeams'))
    # else show the form
    else:
        return render_template('newTeam.html')


@app.route('/team/<int:team_id>/edit/', methods=['GET', 'POST'])
def editTeam(team_id):
    if 'username' not in login_session:
        return redirect('/login')
    team = session.query(Team).filter_by(id=team_id).one()
    editedTeam = session.query(Team).filter_by(id=team_id).one()
    if login_session['user_id'] != team.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit this team. " \
               "Please create your own teams.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        if request.form['name']:
            editedTeam.name = request.form['name']

        if 'file' in request.files:
            file = request.files['file']

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                editedTeam.logo = filename

        session.add(editedTeam)
        session.commit()
        return redirect(url_for('showTeams'))

    else:
        return render_template(
            'editTeam.html', team=editedTeam)


# Delete a Team
@app.route('/team/<int:team_id>/delete/', methods=['GET', 'POST'])
def deleteTeam(team_id):
    if 'username' not in login_session:
        return redirect('/login')
    team = session.query(Team).filter_by(id=team_id).one()
    teamToDelete = session.query(Team).filter_by(id=team_id).one()
    players = session.query(Player).filter_by(team_id=team_id).all()

    if login_session['user_id'] != team.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete this team. " \
               "Please create your own teams.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        for player in players:
            session.delete(player)
        session.delete(teamToDelete)
        flash('%s Successfully Deleted' % teamToDelete.name)
        session.commit()
        return redirect(
            url_for('showTeams', team_id=team_id))
    else:

        return render_template(
            'deleteTeam.html', team=teamToDelete)


# Route with JSON endpoint for all teams
@app.route('/team/JSON')
def teamsJSON():
    teams = session.query(Team).all()
    return jsonify(teams=[r.serialize for r in teams])

# Route with JSON endpoint for players of a team
@app.route('/team/<int:team_id>/player/JSON')
def playersJSON(team_id):
    team = session.query(Team).filter_by(id=team_id).one()
    players = session.query(Player).filter_by(
        team_id=team_id).all()
    return jsonify(Players=[p.serialize for p in players])



# Show a team's players
@app.route('/team/<int:team_id>/')
@app.route('/team/<int:team_id>/player/')
def showPlayers(team_id):
    team = session.query(Team).filter_by(id=team_id).one()
    players = session.query(Player).filter_by(team_id=team_id).all()
    players=session.query(Player).filter_by(
        team_id=team_id).all()
    if 'username' not in login_session:
        return render_template('publicplayers.html', players=players, team=team)
    else:
        return render_template('players.html', players=players, team=team)


# Add a Player in Team
@app.route(
    '/team/<int:team_id>/players/new/', methods=['GET', 'POST'])
def newTeamPlayer(team_id):

    # if user no logged redirect to login
    if 'username' not in login_session:
        return redirect('/login')
    team = session.query(Team).filter_by(id=team_id).one()

    # check if user logged in is owner of player
    if login_session['user_id'] != team.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add player." \
               " Please create your own teams .');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        # Upload File
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        newPlayer = Player(name=request.form['name'], surname=request.form['surname'], role=request.form['role'],
                           picture=filename, team_id=team_id, user_id=team.user_id)
        session.add(newPlayer)
        session.commit()

        return redirect(url_for('showPlayers', team_id=team_id))
    else:
        return render_template('newTeamPlayer.html', team_id=team_id)


# Edit a Player in Team
@app.route('/team/<int:team_id>/player/<int:player_id>/edit',
           methods=['GET', 'POST'])
def editTeamPlayer(team_id, player_id):

    # if user no logged redirect to login
    if 'username' not in login_session:
        return redirect('/login')
    team = session.query(Team).filter_by(id=team_id).one()
    editedPlayer = session.query(Player).filter_by(id=player_id).one()

    # check if user logged in is owner of teaan
    if login_session['user_id'] != team.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit this player." \
               " Please create your own teams.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        if request.form['name']:
            editedPlayer.name = request.form['name']
        if request.form['surname']:
            editedPlayer.surname = request.form['surname']
        if request.form['role']:
            editedPlayer.role = request.form['role']

        if 'file' in request.files:
            file = request.files['file']

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                editedPlayer.picture = filename

        session.add(editedPlayer)
        session.commit()
        return redirect(url_for('showPlayers', team_id=team_id))
    else:

        return render_template(
            'editTeamPlayer.html', team_id=team_id, player_id=player_id, player=editedPlayer)


# Delete a Player in Team
@app.route('/team/<int:team_id>/player/<int:player_id>/delete', methods=['GET', 'POST'])
def deleteTeamPlayer(team_id, player_id):

    # if user no logged redirect to login
    if 'username' not in login_session:
        return redirect('/login')

    # find team and player to delete
    team = session.query(Team).filter_by(id=team_id).one()
    playerToDelete = session.query(Player).filter_by(id=player_id).one()

    # check if user logged is owner of player
    if login_session['user_id'] != team.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete this player. " \
               "Please create your own teams in order to delete players.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        session.delete(playerToDelete)
        session.commit()
        return redirect(url_for('showPlayers', team_id=team_id))
    else:
        return render_template('deleteTeamPlayer.html', player=playerToDelete, team_id=team_id)

# run flask server when script started
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
