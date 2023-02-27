''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Necessary Imports
from fastapi import FastAPI, Request              # The main FastAPI import and Request object
from pydantic import BaseModel                    # Used to define the model matching the DB Schema
from fastapi.responses import HTMLResponse        # Used for returning HTML responses (JSON is default)
from fastapi.templating import Jinja2Templates    # Used for generating HTML from templatized files
from fastapi.staticfiles import StaticFiles       # Used for making static resources available to server
import uvicorn                                    # Used for running the app directly through Python
import pymysql as mysql                   # Used for interacting with the MySQL database
import os                                         # Used for interacting with the system environment
from dotenv import load_dotenv                    # Used to read the credentials

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Configuration
load_dotenv('../credentials.env')                 # Read in the environment variables for MySQL
db_host = 'localhost'
db_user = 'root'
db_pass = 'password'
db_name = 'ece140'

app = FastAPI()                                   # Specify the "app" that will run the routing
views = Jinja2Templates(directory='views')        # Specify where the HTML files are located
static_files = StaticFiles(directory='public')    # Specify where the static files are located
app.mount('/public', static_files, name='public') # Mount the static files directory to /public

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define a User class that matches the SQL schema we defined for our users
class User(BaseModel):
  first_name: str
  last_name: str

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Define helper functions for CRUD operations

# CREATE SQL query
def db_create_user(first_name: str, last_name: str) -> int:
  '''
  1. Open a connection to the database
  2. INSERT a new user into the table
  3. Close the connection to the database
  4. Return the new user's ID (this is stored in the cursor's 'lastrowid' attribute after execution)
  '''
  # Open a connection to the database
  db = mysql.connect(
      host=db_host,
      user=db_user,
      password=db_pass,
      database=db_name
  )

  # Create a cursor object to execute SQL queries
  cursor = db.cursor()

  # Execute the INSERT query to create a new user
  insert_query = "INSERT INTO users (first_name, last_name) VALUES (%s, %s)"
  values = (first_name, last_name)
  cursor.execute(insert_query, values)

  # Get the ID of the new user
  user_id = cursor.lastrowid

  # Commit the changes to the database and close the connection
  db.commit()
  db.close()

  # Return the new user's ID
  return user_id

# SELECT SQL query
def db_select_users(user_id: int = None) -> list:
  '''
  1. Open a connection to the database
  2. If the user_id is specified as an argument, perform a SELECT for just that user record
  3. If there is no user_id specified, then perform a SELECT for all users
  4. Close the connection to the database
  5. Return the retrieved record(s)
  '''
  # Open a connection to the database
  db = mysql.connect(
      host=db_host,
      user=db_user,
      password=db_pass,
      database=db_name
  )

  # Create a cursor object to execute SQL queries
  cursor = db.cursor()

  # Execute the SELECT query to retrieve user records
  if user_id is not None:
    select_query = "SELECT * FROM users WHERE id=%s"
    values = (user_id,)
    cursor.execute(select_query, values)
  else:
    select_query = "SELECT * FROM users"
    cursor.execute(select_query)

  # Fetch the retrieved record(s)
  records = cursor.fetchall()

  # Close the connection to the database
  db.close()

  # Return the retrieved record(s)
  return records


# UPDATE SQL query
def db_update_user(user_id:int, first_name:str, last_name:str) -> bool:
  '''
  1. Open a connection to the database
  2. UPDATE the user in the database
  3. Close the connection to the database
  4. Return True if a row in the database was successfully updated and False otherwise (you can
     check how many records were affected by looking at the cursor's 'rowcount' attribute)
  '''
  try:
    conn = mysql.connect(host=db_host, user=db_user, password=db_pass, database=db_name)
    cursor = conn.cursor()
    delete_query = f"DELETE FROM users WHERE id = {user_id}"
    cursor.execute(delete_query)
    conn.commit()
    conn.close()
    return cursor.rowcount == 1
  
  except Exception as e:
    print(f"Error deleting user {user_id}: {e}")
    return False


# DELETE SQL query
def db_delete_user(user_id: int) -> bool:
  '''
  1. Open a connection to the database
  2. DELETE the user in the database
  3. Close the connection to the database
  4. Return True if a row in the database was successfully deleted and False otherwise (you can
     check how many records were affected by looking at the cursor's 'rowcount' attribute)
  '''
  # Open a connection to the database
  db = mysql.connect(
      host=db_host,
      user=db_user,
      password=db_pass,
      database=db_name
  )

  # Create a cursor object to execute SQL queries
  cursor = db.cursor()

  # Execute the DELETE query to remove the user
  delete_query = "DELETE FROM users WHERE id = %s"
  values = (user_id,)
  cursor.execute(delete_query, values)

  # Check how many rows were affected by the DELETE query
  rowcount = cursor.rowcount

  # Commit the changes to the database and close the connection
  db.commit()
  db.close()

  # Return True if a row was deleted, False otherwise
  return rowcount > 0


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Home route to load the main page in a templatized fashion

# GET /
@app.get('/', response_class=HTMLResponse)
def get_home(request:Request) -> HTMLResponse:
  return views.TemplateResponse('index.html', {'request':request, 'users':db_select_users()})

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# RESTful User Routes

# GET /users
# Used to query a collection of all users
@app.get('/users')
def get_users() -> dict:
  '''
  1. Query the database for all users
  2. Format the results as a list of dictionaries (JSON objects!) where the dictionary keys are:
    'id', 'first_name', and 'last_name'
  3. Return this collection as a JSON object, where the key is 'users' and the value is the list
  '''
  # Open a connection to the database
  db = mysql.connect(
      host=db_host,
      user=db_user,
      password=db_pass,
      database=db_name
  )

  # Create a cursor object to execute SQL queries
  cursor = db.cursor()

  # Execute the SELECT query to retrieve all users
  select_query = "SELECT id, first_name, last_name FROM users"
  cursor.execute(select_query)

  # Retrieve the results of the query as a list of tuples
  results = cursor.fetchall()

  # Format the results as a list of dictionaries
  users = [{'id': row[0], 'first_name': row[1], 'last_name': row[2]}
           for row in results]

  # Close the connection to the database
  db.close()

  # Return the list of users as a JSON object
  return {'users': users}


# GET /users/{user_id}
# Used to query a single user
@app.get('/users/{user_id}')
def get_user(user_id: int) -> dict:
  '''
  1. Query the database for the user with a database ID of 'user_id'
  2. If the user does not exist, return an empty object
  3. Otherwise, format the result as JSON where the keys are: 'id', 'first_name', and 'last_name'
  4. Return this object
  '''
  # Open a connection to the database
  db = mysql.connect(
      host=db_host,
      user=db_user,
      password=db_pass,
      database=db_name
  )

  # Create a cursor object to execute SQL queries
  cursor = db.cursor()

  # Execute the SELECT query to retrieve the user with the specified ID
  select_query = "SELECT * FROM users WHERE id = %s"
  values = (user_id,)
  cursor.execute(select_query, values)

  # Fetch the result of the query
  result = cursor.fetchone()

  # Close the connection to the database
  db.close()

  # If the user does not exist, return an empty object
  if not result:
      return {}

  # Otherwise, format the result as JSON
  user = {
      'id': result[0],
      'first_name': result[1],
      'last_name': result[2]
  }

  return user


# POST /users
# Used to create a new user
@app.post("/users", response_class=HTMLResponse)
def post_user(request: Request, user: User) -> dict:
  '''
  1. Retrieve the data asynchronously from the 'request' object
  2. Extract the first and last name from the POST body
  3. Create a new user in the database
  4. Return the user record back to the client as JSON
  '''
  # Extract the first and last name from the POST body
  first_name = user.first_name
  last_name = user.last_name

  # Create a new user in the database
  user_id = db_create_user(first_name, last_name)

  # Return the user record back to the client as JSON
  return {"user_id": user_id, "first_name": first_name, "last_name": last_name}

# PUT /users/{user_id}


@app.put('/users/{user_id}')
def put_user(user_id: int, user: User) -> dict:
  '''
  1. Retrieve the data asynchronously from the 'request' object
  2. Attempt to update the user first and last name in the database
  3. Return the update status under the 'success' key
  '''
  # Open a connection to the database
  db = mysql.connect(
      host=db_host,
      user=db_user,
      password=db_pass,
      database=db_name
  )

  # Create a cursor object to execute SQL queries
  cursor = db.cursor()

  # Execute the UPDATE query to update the user's first name and last name
  update_query = "UPDATE users SET first_name=%s, last_name=%s WHERE id=%s"
  values = (user.first_name, user.last_name, user_id)
  cursor.execute(update_query, values)

  # Commit the changes to the database and close the connection
  db.commit()
  db.close()

  # Return the update status under the 'success' key
  return {'success': True}


# DELETE /users/{user_id}
@app.delete('/users/{user_id}')
def delete_user(user_id: int) -> dict:
  '''
  1. Attempt to delete the user from the database
  2. Return the delete status under the 'success' key
  '''
  # Open a connection to the database
  db = mysql.connect(
      host=db_host,
      user=db_user,
      password=db_pass,
      database=db_name
  )

  # Create a cursor object to execute SQL queries
  cursor = db.cursor()

  # Execute the DELETE query to remove the user with the specified ID
  delete_query = "DELETE FROM users WHERE id=%s"
  values = (user_id,)
  cursor.execute(delete_query, values)

  # Check if the user was successfully deleted and set the success flag accordingly
  if cursor.rowcount == 1:
      success = True
  else:
      success = False

  # Commit the changes to the database and close the connection
  db.commit()
  db.close()

  # Return the delete status
  return {'success': success}


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# If running the server directly from Python as a module
if __name__ == "__main__":
  uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)