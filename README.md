# finTrack #
This is a financial tracking system developed in Flask.

## Prerequisite: ##
It's better to have Python 3 installed
* The application will be ran in the virtual environment (the following steps are for MacOS X)
  1. Create a project forlder, and within the project folder, create the ***venv*** folder: *python3 -m venv venv*
  2. Activate the environment before you work on your project using: *. venv/bin/activate* (use deactivate to exit virtual)
  3. Within the activated environment, use the following command to install Flask: *pip install Flask*

## Database ##
The 'DROP TABLE IF EXIST tablename' statement in 'schema.sql' means if the table exist then drop the table.
To initialize the database, run **flask init-db** (This command also erase all the existing data). 

## To run the application ##

export FLASK_APP=finTrack   
export FLASK_ENV=development    
flask run   
flask run --host=0.0.0.0    

export SECRET_EMAILP='your from email password'

The email service python code cannot be saved as 'email.py', because the email.py will prevent the services from smtplib to be working.
