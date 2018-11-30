from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash

from sqlalchemy import create_engine, asc
from sqlalchemy import sessionmaker
from database_setup import Base, User, Company, Camera

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open("client_secret.json", "r").read())["web"]["client_id"]

# Connect to database and create database session
engine = create_engine('sqlite:///camerastudio.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a state token to prevent request forgery
# Store it in the session for later use
@app.route('/login')
def showLogin():
    # Create a random 32 character string with a mix of uppercase letter and digits
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x
        in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" %login_session['state']

    # Render the Login template
    return render_template('login.html', STATE=state)

# Verify the state token
@app.route('/gconnect', methods=['POST'])
def gConnect():
    # If the tokens don't match return a 401 error
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the auth code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json_dumps('Failed to upgrade the auth code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    # Verify the access token
    url = ('https://www.googleapis.com/oauth2/v2/tokeninfo?access_token=%s'
        % access_token)

    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is for the correct user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(result.get('Token users do not match')), 401)
        response.header['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is for the correct app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(result.get('Token apps do not match')), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if user already logged-in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id     = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(result.get('Current user is already logged-in')), 200)
        response.header['Content-Type'] = 'application/json'
    # Store the user credentials
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id
    # Okay, everything checks out now lets get some user details
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    # Store the user details in the session
    login_session['username']   = data["name"]
    login_session['picture']    = data["picture"]
    login_session['email']      = data["email"]

    # Create User unless it is already stored; store user_id
    user_id = getUserID(login_session['email'])
    if user_id == None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    # Now return the user details as HTML
    # TODO: just hand the value only not an HTML itself
    output = ""
    output += "<h1>Welcome, "
    output += login_session['username']
    output += "!</h1>"
    output += "<img src='"
    output += login_session['picture']
    output += "' style = 'width: 300px; height: 300px; border-radius: 150 px;"
    output += " -webkit-border-radius: 150px; -moz-border-radius: 150px;'>"
    flash("You are now logged in as %s" % login_session['username'])
    return output

# User helper functions

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

# Revoke the access token and reset the login_session
@app.route('/logout')
def logout():
    if 'username' not in login_session:
        return redirect(url_for('#'))
        # return redirect(url_for('showCompany'))

    stored_username = login_session.get('username')
    # print("In logout, current user is '%s'" % stored_username)
    stored_access_token = login_session.get('access_token')
    # Only all connected users to log out
    if stored_access_token is None:
        print("In logout, access token for user '%s' is None!" % stored_username)
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Revoke the access token
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s' % stored_access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # print("In logout, revoke result = ", result)
    if result['status'] == '200':
        print("In logout, user '%s' successfully logged out" % stored_username)
        # Reset the user's session
        del login_session['access_token']
       del login_session['gplus_id']
       del login_session['username']
       del login_session['picture']
       del login_session['email']
       del login_session['user_id']
       # response = make_response(json.dumps('Current user logged out.'), 200)
       # response.headers['Content-Type'] = 'application/json'
       # return response

       # Send a notification message
       flash('Current user logged out.')
       return redirect(url_for('#'))
       # return redirect(url_for('showCompany'))
   else:
       print("In logout, failed to revoke token for user '%s' response was '%s'" % (stored_username, result['status']))
       # Send a failure message
       response = make_response(json.dumps('Failed to revoke token for current use.'), 400)
       response.headers['Content-Type'] = 'application/json'
       return response

# ^^^^^^^^^^^^^^^^^^^^ Auth ^^^^^^^^^^^^^^^^^^^^

# JSON APIs to view Company & Camera Information

# return all company information
@app.route('/company/JSON')
def companiesJson():
    companies = session.query(Company).all()
    return jsonify(companies = [r.serialize for r in companies])

# return one specific company information
@app.route('/company/<int:company_id>/JSON')
def companyJson():
    company = session.query(Company).filter_by(id = company_id).one()
    return jsonify(company = [r.serialize for r in company])

# return all camera information which belong to one company
@app.route('/company/<int:company_id>/camera/JSON')
def companyCameraJson():
    cameras = session.query(Camera).filter_by(company_id = company_id).all()
    return jsonify(company = [r.serialize for r in company])

# return all camera information regardless what company they belonged to
@app.route('/camera/JSON')
def camerasJson():
    cameras = session.query(Camera).all()
    return jsonify(cameras = [r.serialize for r in cameras])

# return one specific camera information
@app.route('/camera/<int:camera_id>/JSON')
def cameraJson():
    camera = session.query(Camera).filter_by(id = camera_id).one()
    return jsonify(camera = [r.serialize for r in camera])

# ^^^^^^^^^^^^^^^^^^^^ API ^^^^^^^^^^^^^^^^^^^^

# Show all Companies
@app.route('/')
@app.route('/index')
@app.route('/company')
def showCompany():
    companies = session.query(Company).order_by(asc(Company.name))
    if 'username' not in login_session:
        return render_template('publicCompany.html', companies = companies)
    return render_template('companies.html', companies = companies)

# Create a new Company
@app.route('/company/new', methods=['GET','POST'])
def createCompany():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newCompany = Company(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCompany)
        flash('Company "%s" successfully created' % newCompany.name)
        session.commit()
        return redirect(url_for('showCompany'))
    else:
        return render_template('createCompany.html')

# Edit a Company
@app.route('/company/<int:company_id>/edit', methods=['GET','POST'])
def editCompany(company_id):
    if 'username' not in login_session:
        return redirect('/login')

    editedCompany = session.query(Company).filter_by(id=company_id).one()
    if login_session['user_id'] != editedCompany.user_id:
        return "<script>function myAlert() { alert('You are not authorized to edit this company.'); }</script><body onload='myAlert()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedCompany.name = request.form['name']
            flash('Company "%s" successfully edited' % editedCompany.name)
            return redirect_url(url_for('showCompany'))
    else:
        return render_template('editCompany.html', company = editedCompany)

# Delete a Company
@app.route('/company/<int:company_id>/delete', methods=['GET','POST'])
def deleteCompany(company_id):
    if 'username' not in login_session:
        return redirect('/login')

    companyToDelete = session.query(Company).filter_by(id=company_id).one()
    if login_session['user_id'] != companyToDelete.user_id:
        return "<script>function myAlert() { alert('You are not authorized to edit this company.'); }</script><body onload='myAlert()'>"
    if request.method == 'POST':
        session.delete(companyToDelete)
        flash('Company "%s" successfully deleted' % companyToDelete.name)
        session.commit()
        return redirect(url_for('showCompany', company_id = company_id))
    else:
        return render_template('deleteCompany.html', company = companyToDelete)

# ^^^^^^^^^^^^^^^^^^^^ Company Routing ^^^^^^^^^^^^^^^^^^^^

# TODO: Creating Camera routing info and make comment

# Show all Cameras
@app.route('/company/<int:company_id>')
@app.route('/company/<int:company_id>/camera')
def showCamera(company_id):
    company = session.query(Company).filter_by(id=company_id).one()
    cameras = session.query(Camera).filter_by(company_id=company_id).all()
    creator = getUserInfo(company.user_id)
    # Only show the non-public version if the user is logged-in and its creator
    if 'username' not in login_session or login_session['user_id'] != creator.id:
        return render_template('publicCamera.html', cameras=cameras, company=company, creator=creator)
    return render_template('cameras.html', cameras=cameras, company=company, creator=creator)

# Create a new camera
@app.route('/company/<int:company_id>/camera/new', methods=['GET','POST'])
def newCamera(company_id):
    if 'username' not in login_session:
        return redirect('/login')

    company = session.query(Company).filter_by(id=company_id).one()
    if login_session['user_id'] != company.user_id:
        return "<script>function myAlert() { alert('You are not authorized to add an item to this camera.'); }</script><body onload='myAlert()'>"
    if request.method == 'POST':
        newCamera = Camera(name=request.form['name'], description=request.form['description'], price=request.form['price'], company_id=company_id, user_id=company.user_id)
        user_id = login_session['user_id']
        session.commit()
        flash('Company "%s" successfully created' % (newCamera.name))
        return redirect(url_for('showCamera', company_id = company_id))
    else:
        return render_template('newCamera.html', company_id=company_id)

# Edit a company
@app.route('/company/<int:company_id>/camera/<int:camera_id>/edit', methods=['GET','POST'])
def editCamera(company_id, camera_id):
    if 'username' not in login_session:
        return redirect('/login')

    editedCamera = session.query(Camera).filter_by(id=camera_id).one()
    company = session.query(Company).filter_by(id=company_id).one()
    if login_session['user_id'] != editedCamera.user_id:
        return "<script>function myAlert() { alert('You are not authorized to add an item to this camera.'); }</script><body onload='myAlert()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedCamera.name = request.form['name']
        if request.form['description']:
            editedCamera.description = request.form['description']
        if request.form['price']:
            editedCamera.price = request.form['price']
        session.add(editedCamera)
        session.commit()
        flash('Company "%s" successfully edited' % editedCamera.name)
        return redirect(url_for('showCamera', company_id=company_id))
    else:
        return render_template('editCamera.html', company_id=company_id, camera_id=camera_id, editedCamera = editedCamera)

# Delete a camera
@app.route('/company/<int:compant_id>/camera/<int:camera_id>/delete', methods=['GET','POST'])
def deleteCamera(company_id, camera_id):
    if 'username' not in login_session:
        return redirect('/login')

    company = session.query(Company).filter_by(id=company_id).one()
    itemToDelete = session.query(Camera).filter_by(id=camera_id).one()
    if login_session['user_id'] != itemToDelete.user_id:
        return "<script>function myAlert() { alert('You are not authorized to delete this camera.'); }</script><body onload='myAlert()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Camera Item "%s" successfully deleted' % itemToDelete.name)
        return redirect(url_for('showCamera', company_id=company_id))
    else:
        return render_template('deleteCamera.html', item=itemToDelete)


# ^^^^^^^^^^^^^^^^^^^^ Camera Routing ^^^^^^^^^^^^^^^^^^^^

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port = 5000)
