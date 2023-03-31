
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "ax2155"
DATABASE_PASSWRD = "ODQyMg"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# with engine.connect() as conn:
# 	create_table_command = """
# 	CREATE TABLE IF NOT EXISTS test (
# 		id serial,
# 		name text
# 	)
# 	"""
# 	res = conn.execute(text(create_table_command))
# 	insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
# 	res = conn.execute(text(insert_table_command))
# 	# you need to commit for create, insert, update queries to reflect
# 	conn.commit()


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	"""


	#
	return render_template("index.html")

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
	return render_template("another.html")

@app.route('/new')
def new():
	return render_template("new.html")


@app.route('/about')
def about():
	return render_template("about.html")


@app.route('/hour')
def hour():
	return render_template("hour.html")

@app.route('/query')
def query():
	cursor = []
	select_building = "SELECT code from building"
	select_dept = "SELECT dept_id from department"
	cursor.append(g.conn.execute(text(select_building)))
	cursor.append(g.conn.execute(text(select_dept)))
	names = []
	department = []
	for result in cursor[0]:
		names.append(result[0])
	for result in cursor[1]:
		department.append(result[0])
	for c in cursor:
		c.close()
	context = dict(building=names, department=department)

	return render_template("query.html", **context)


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
	# accessing form inputs from user
	id = request.form['id']
	event_name = request.form['name']
	intro = request.form['introduction']
	description = request.form['description']
	date_of_choice = request.form['date']
	dept_id = request.form['dept_id']
	building = request.form['building']
	code = request.form['code']
	start_hour = request.form['hour']

	# passing params in for each variable into query
	params = {}
	params["id"] = id
	params["event_name"] = event_name
	params["intro"] = intro
	params["description"] = description
	params["date_of_choice"] = date_of_choice
	params["dept_id"] = dept_id
	params["building"] = building
	params["code"] = int(code)
	params["start_hour"] = int(start_hour)

	# check whether the prefered room exists: if not, build it
	hours = g.conn.execute(text(f'select start_time from loc_occupancy where building=:building and code=:code and date_occupied=:date_of_choice'), params)
	room = g.conn.execute(text(f'select * from location where building=:building and code=:code'), params)
	if room.rowcount == 0:
		g.conn.execute(text(
			'INSERT INTO location(building, code) VALUES (:building, :code)'), params)
	# check whether there is an hour conflict: if yes, lead to hour page
	for h in hours:
		if start_hour == h[0]:
			return redirect('/hour')
	else:
		# 1. Insert into Location Occupancy
		try:
			g.conn.execute(text('INSERT INTO loc_occupancy(building, code, date_occupied, start_time) VALUES (:building, :code, :date_of_choice, :start_hour)'), params)
		except:
			return redirect('/hour')
		# 2. Insert into Events
		g.conn.execute(text('INSERT INTO Events(event_id, name_event, introduction, description, date, dept_id, building, code) VALUES (:id, :event_name, :intro, :description, :date_of_choice, :dept_id, :building, :code)'), params)
		# 3. Insert into Event Occupancy
		g.conn.execute(text('INSERT INTO Event_occupancy(event_id, start_time) VALUES (:id, :start_hour)'), params)
		g.conn.commit()
		return redirect('/')


@app.route('/display', methods=['POST'])
def display():


	#event = {'id': None, 'name': None, 'intro': None, 'description': None,'room': None, 'date': None, 'hour': None}

	event_name = request.form['name']
	match = request.form['match']
	build = request.form['build']
	dept = request.form['dept']
	date = request.form['startdate']

	params = {}
	params["event_name"] = event_name
	params["build"] = build
	params["dept"] = dept
	params["date_s"] = date


	if len(event_name) == 0:
		select_criteria = 'WHERE Events.event_id=event_occupancy.event_id'
		if dept != 'ANY':
			select_criteria += ' and dept_id=:dept '
		if build != 'ANY':
			select_criteria += ' and Events.building=:build '
		if date != '':
			select_criteria += ' and Events.date=:date_s'
		if select_criteria == 'WHERE Events.event_id=event_occupancy.event_id':
			select_criteria = ''
	elif match == 'exact':
		select_criteria = 'WHERE name_event=:event_name '
		if dept != 'ANY':
			select_criteria += ' and dept_id=:dept '
		if build != 'ANY':
			select_criteria += ' and Events.building=:build '
		if date != '':
			select_criteria += ' and Events.date=:date_s'
	else:
		params['event_name'] = f'%{event_name}%'
		select_criteria = 'WHERE name_event like :event_name'
		if dept != 'ANY':
			select_criteria += ' and dept_id=:dept '
		if build != 'ANY':
			select_criteria += ' and Events.building=:build '
		if date != '':
			select_criteria += ' and Events.date=:date_s'

	exe = f'SELECT DISTINCT Events.event_id, Events.name_event,Events.introduction, ' \
		  f'Events.description, building.link, Events.code, ' \
		  f'building.fullname, Events.date, ' \
		  f'event_occupancy.start_time, department.dept_name ' \
		  f'FROM EVENTS left join event_occupancy using(event_id) ' \
		  f'left join building on EVENTS.building=building.code ' \
		  f'left join department using(dept_id) ' \
		  f'{select_criteria}'

	cursor = g.conn.execute(text(exe), params)
	# if len(event_name) == 0:
	# 	cursor = g.conn.execute(text('SELECT DISTINCT Events.event_id, Events.name_event,Events.introduction, '
	# 								 'Events.description, building.link, Events.code, '
	# 								 'building.fullname, Events.date, '
	# 								 'event_occupancy.start_time, department.dept_name '
	# 								 'FROM EVENTS left join event_occupancy using(event_id) '
	# 								 'left join building on EVENTS.building=building.code '
	# 								 'left join department using(dept_id) '
	# 								 'WHERE'
	# 								 ' Events.building=:build and dept_id=:dept and Events.date=:date_s'), params)
	#
	# else:
	# 	if match == 'exact':
	# 		cursor = g.conn.execute(text('SELECT DISTINCT Events.event_id, Events.name_event,Events.introduction, '
	# 									 'Events.description, building.link, Events.code, '
	# 									 'building.fullname, Events.date, '
	# 									 'event_occupancy.start_time, department.dept_name '
	# 									 'FROM EVENTS left join event_occupancy using(event_id) '
	# 									 'left join building on EVENTS.building=building.code '
	# 									 'left join department using(dept_id) '
	# 									 'WHERE '
	# 									 'name_event=:event_name and '
	# 									 'Events.building=:build and dept_id=:dept and Events.date=:date_s'), params)
	# 	else:
	# 		params['event_name'] = f'%{event_name}%'
	# 		cursor = g.conn.execute(text('SELECT DISTINCT Events.event_id, Events.name_event,Events.introduction, '
	# 									 'Events.description, building.link, Events.code, '
	# 									 'building.fullname, Events.date, '
	# 									 'event_occupancy.start_time, department.dept_name '
	# 									 'FROM EVENTS left join event_occupancy using(event_id) '
	# 									 'left join building on EVENTS.building=building.code '
	# 									 'left join department using(dept_id) '
	# 									 'WHERE '
	# 									 'name_event like :event_name and '
	# 									 'EVENTS.building=:build and dept_id=:dept and Events.date=:date_s'), params)

	events = []
	for e in cursor:
		event = {'id': None, 'name': None, 'intro': None, 'description': None, 'blink': None, 'room': None,
				 'bfname': None,
				 'date': None, 'hour': None, 'dfname': None}
		for _ in range(len(event.keys())):
			event[list(event.keys())[_]] = e[_]
		events.append(event)

	cursor.close()

	# might be removed if there is a map from building to blink, bfname, and from dept to dfname
	# for e in events:
	# 	e['bfname'] = None
	# 	e['blink'] = None
	# 	e['dfname'] = None

	context = dict(a_list=events)


	return render_template("display.html", **context)




@app.route('/login')
def login():
	abort(401)
	this_is_never_executed()




if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
