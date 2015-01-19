#!/usr/bin/python

from __future__ import print_function

from sqlalchemy.event import listens_for
from sqlalchemy.pool import Pool
from sqlalchemy.orm import sessionmaker, scoped_session

from DatabaseConnection import DatabaseConnection


'''
Notes:
This file must be 'import'ed BEFORE "DatabaseConnection".

If the SQLite database you specify below doesn't exist, a new
database will be created for you. This means if specify a different
path, the script won't fail with "database not found", but rather
you will get a "table not found" error since you've created a new database.
'''

# Fill in database connection information here.
sqlite_db = {
	'name'	: 'Stars.sqlite' # this is the name of the file
}

# For more options of SQLite connection strings, see:
# http://www.sqlalchemy.org/docs/reference/dialects/sqlite.html#connect-strings

db_connection_string = "sqlite:///%s" % sqlite_db['name']

# ------------ Do not edit anything below this line! -------------------------

@listens_for(Pool, 'connect') #, once=True) # needs 0.9.4
def _fk_pragma_on_connect(dbapi_con, connection_record):
	print("This is being called.")
	dbapi_con.execute('pragma foreign_keys=ON')


# This allows the file to be 'import'ed any number of times, but attempts to
# connect to the database only once.
try:
	db = DatabaseConnection() # fails if connection not yet made.
except:
	db = DatabaseConnection(database_connection_string=db_connection_string)

engine = db.engine

# SQLAlchemy has foreign key support starting with version 3.6.19.
# However, it must be enabled every time a database is opened.
# This code will do that.
# ----------------------------------------------------------------
#def _fk_pragma_on_connect(dbapi_con, con_record):
#	print("This is being called.")
#	dbapi_con.execute('pragma foreign_keys=ON')
#
#sqlalchemy.event.listen(db.engine, 'connect', _fk_pragma_on_connect)
# ----------------------------------------------------------------

metadata = db.metadata
#Session = sessionmaker(bind=engine, autocommit=True, autoflush=False)
Session = scoped_session(sessionmaker(bind=engine, autocommit=True, autoflush=False))

