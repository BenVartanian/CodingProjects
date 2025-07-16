from datetime import timedelta
import mysql.connector as mysql
import hashlib
import random
import string
from flask import Flask, redirect, url_for, request, render_template, render_template_string, session

#Flask variables
app = Flask(__name__)
app.secret_key = 'loginsecretkey'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)

#DB Variables
host = "localhost"
user = "root"
password = "mysqlrootpassword" #Not a great idea to store passwords in source code. This is a demo but a more secure method should be used.
database = "logins" #This should be whatever you've named the schema you're working in
insert = ("insert into login (username, password, salt) "
          "values (%s, %s, %s)")

#Security Methods
def hashastring(passwordstring): #Creates a hash of a string (user password)
    hash = hashlib.sha256()
    hash.update(passwordstring.encode())
    finalHash = hash.hexdigest()
    return finalHash

def generateSalt(): #Creates a random group of letters for use in obscuring user passwords
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for i in range(8))
    return random_string

def checkValidCharacters(stringToCheck): #Some server side input sanitization just in case something slips past client-sided validiation.
    invalidChars = ['/', '\\', '{', '}', '|', '^', '=', '+', '<','>','#', '$', '%','&','*',"'", '"', ':', ';', '~', '_', '-', '!']
    for char in invalidChars:
        if char in stringToCheck:
            return False
    return True



#Init web server
@app.route('/') #Default path of the webpage, defines what should happen upon users typing http://localhost:5000/
def base():
    if not session.get("Name"):
        return redirect('/login')
    return redirect('/secure')

@app.route('/secure', methods = ['GET', 'POST']) #Secure path of the web server, defines methods at http://localhost:5000/secure
def secure():
    if request.method == 'POST':
        session["Name"] = None
        return redirect("/")
    if request.method == 'GET':
        if not session.get("Name"):
            return redirect('error')
        return render_template('SecurePage.html')

@app.route('/login', methods=['POST', 'GET']) #Login path of the web server, defines methods at http://localhost:5000/login
def login():
    if session.get("Name"): #Check if a session exists, if it does when accessing this page we want to clear it
        session["Name"] = None
    if request.method == 'POST': #Post indicates someone's submitted a login form
        user = str(request.form['Username'])
        userPassword = str(request.form['Password'])
        #4 lines below this ensure neither username or password contains invalid characters
        if not checkValidCharacters(user):
            return render_template('FaultyLogin.html')
        if not checkValidCharacters(userPassword):
            return render_template('FaultyLogin.html')
        try:
            #Following 6 lines of code get username, salt, and password from DB. Keep in mind that the password retrieved has been salted and hashed
            sqlStatement = f'Select password from login where username = "{user}"'
            command_handler.execute(sqlStatement)
            storedPass = str(command_handler.fetchone()[0])
            command_handler.execute(f'Select salt from login where username = "{user}"')
            storedSalt = str(command_handler.fetchone()[0])
            #We'll salt the password the user enters and hash it to see if it matches the salted and hashed password stored
            #If it does log the user in.
            hexedUserPassword = hashastring(userPassword + storedSalt)
        except Exception as ex:
            storedPass = '0'
            hexedUserPassword = 'problem'
        if storedPass == hexedUserPassword:
            #And issue them a cookie
            session["Name"] = request.form.get("Username")
            session.permanent = True
            return redirect('/')
        else:
            return render_template('FaultyLogin.html')
    if request.method == 'GET':
        return render_template('LoginPage.html')

@app.route('/create_account', methods=['POST', 'GET']) #Create account path, defines methods for http://localhost:5000/create_account
def create_account():
    if request.method == 'POST':
        createAccountUser = str(request.form['Username'])
        createAccountPassword = str(request.form['Password'])
        #4 lines below check to ensure no invalid characters are present in either username or password
        if not checkValidCharacters(createAccountUser):
            return render_template('FaultyAccountCreation.html')
        if not checkValidCharacters(createAccountPassword):
            return render_template('FaultyAccountCreation.html')
        try:
            #Statements below will return None object if the username isn't in the database
            sqlStatement = f'Select userId from login where username = "{createAccountUser}"'
            command_handler.execute(sqlStatement)
            userExists = type(command_handler.fetchone())
        except Exception as ex:
            print("Error checking database")
        if str(userExists) != "<class 'NoneType'>": #If the username is already taken, print to the webpage that it is
            return render_template('UsernameTaken.html')
        else:
            #Otherwise we're going to add it to the database, the username and salt as plaintext but the password as a salted and hashed value.
            salt = generateSalt()
            saltedAndHashedPassword = hashastring(createAccountPassword + salt)
            accountCreationString = f'Insert into login (username, password, salt) values ("{createAccountUser}", "{saltedAndHashedPassword}", "{salt}")'
            command_handler.execute(accountCreationString)
            db.commit()
            return redirect('/account_created')
    return redirect('error')

@app.route('/account_created', methods = ['GET']) #Account created path, defines methods for http://localhost:5000/account_created
def account_created():
    if request.method == 'GET':
        return render_template('account_created.html')
    return redirect('error')

@app.route('/error', methods = ['GET'])#Error path
def error():
    if request.method != 'GET':
        return redirect('/login')
    else:
        return render_template('Intermediary.html')

@app.route('/<path:my_path>', methods = ['GET', 'POST'])#This route catches all undefined paths under the same error umbrella to prevent giving away what webpages are valid
def catch_all(my_path):
    if request.method == 'GET' or request.method == 'POST':
        return redirect('error')
    return redirect('error')

#Make Connection
try:
    db = mysql.connect(host=host, user = user, password = password, database = database)
    print("connected")
except Exception as e:
    print("failed to connect")


#Access db
try:
    command_handler = db.cursor()

except Exception as e:
    print("cursor wasn't created")

app.run()