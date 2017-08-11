from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import re
import md5 # imports the md5 module to generate a hash

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'[0-9]')
PASS_REGEX = re.compile(r'.*[A-Z].*[0-9]')

app = Flask(__name__)
app.secret_key = "ThisIsSecretadfasdfasdf!"

mysql = MySQLConnector(app,'login_reg')

@app.route('/')
def index():
    print session
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register_user():
    input_email = request.form['email']
    email_query = "SELECT * FROM users WHERE email = :email_id"
    query_data = {'email_id': input_email}
    stored_email = mysql.query_db(email_query, query_data)
    # print stored_email[0]['email']

    print request.form
    print request.form['email']
    print session

    for x in request.form:
        if len(request.form[x]) < 1:
            flash(x + " cannot be blank!", 'blank')
    
    # if not request.form['first_name'].isalpha():
    if NAME_REGEX.search(request.form['first_name']):
        flash("First name cannot contain any numbers", 'error')
    if NAME_REGEX.search(request.form['last_name']):
        flash("Last name cannot contain any numbers", 'error')

    if len(request.form['password']) < 8:
        flash("Password must be more than 8 characters", 'password')

    if not EMAIL_REGEX.match(request.form['email']):
        flash("Email must be a valid email", 'error')
    
    if not PASS_REGEX.search(request.form['password']):
        flash("Password must have a number and an uppercase letter", 'password')
    
    if request.form['password'] != request.form['confirm_password']:
        flash("Password and Password Confirmation should match", 'password')
    if stored_email:
        flash("Email already exists!")

# The line below is key so you get all of the error messages to display on the first page and then the all good message if no flashes, all good is another flash
    if '_flashes' in session:
# changed this line to be render so I could put in value = on the html page to save what the person typed when it didn't validate
        return redirect('/')
    else:
        flash("All Good!!!!", 'good')
        query = "INSERT INTO users (f_name, l_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email_id, :pass, NOW(), NOW())"
        # We'll then create a dictionary of data from the POST data received.
        data = {
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'email_id': request.form['email'],
                'pass': md5.new(request.form['password']).hexdigest()
            }
        # Run query, with dictionary values injected into the query.
        mysql.query_db(query, data)

        input_email = request.form['email']
        email_query = "SELECT * FROM users WHERE email = :email_id"
        query_data = {'email_id': input_email}
        stored_email = mysql.query_db(email_query, query_data)

        session['user_id'] = stored_email[0]['id']

        flash("This email address you entered " + input_email + " is a valid email address. Thank you!")
        return redirect('/success')
#didn't get the hacker version done with the birthday stuff

@app.route('/success')
def success():
    query = "SELECT email, DATE_FORMAT(created_at,'%M %d %Y') as date FROM users"       # define your query, make sure you use the DATE_FORMAT stuff in your key 
    emails = mysql.query_db(query)

    id_query = "SELECT * FROM users WHERE id = :user_id"
    query_data = {'user_id': session['user_id']}
    name_query = mysql.query_db(id_query, query_data)

    print session
    return render_template('success.html', email_list = emails, firname = name_query[0]['f_name'])

@app.route('/login', methods=['POST'])
def login():

    input_email = request.form['email']
    input_password = request.form['password']
    email_query = "SELECT * FROM users WHERE email = :email_id"
    query_data = {'email_id': input_email}
    stored_email = mysql.query_db(email_query, query_data)

    if not EMAIL_REGEX.match(request.form['email']):
        flash("Email must be a valid email", 'error')

    if not stored_email:
        flash("User does not exist!")
        return redirect('/')

    else:
        if md5.new(request.form['password']).hexdigest() == stored_email[0]['password']:
            session['user_id'] = stored_email[0]['id']
            return redirect('/success')
        else:
            flash("Wrong password, try again!")
            return redirect('/')


#     if '_flashes' in session:
# # changed this line to be render so I could put in value = on the html page to save what the person typed when it didn't validate
#         return redirect('/')




app.run(debug=True)