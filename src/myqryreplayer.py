#!/usr/bin/python

import optparse
import re
import sys
import MySQLdb
import time
import getpass

qry_file = '/var/log/mysql/mysql.log';

parser = optparse.OptionParser(add_help_option=False)
parser.set_usage(sys.argv[0] + " [option] <DATABASE> <SESSION_ID>")

parser.add_option("-V", "--verbose", dest="verbose", action="store_true", default=False, help="Show more output")
parser.add_option("-l", "--logfile", dest="logfile", action="store", default="/var/log/mysql/mysql.log", help="Path to the MySQL query log file")
parser.add_option("-u", dest="username", action="store", default="", help="MySQL Username")
parser.add_option("-h", "--hostname", dest="hostname", action="store", default="localhost", help="MySQL Hostname")
parser.add_option("-p", dest="password", action="store", default="", help="MySQL Password")
parser.add_option("--all", dest="all", action="store_true", default=False, help="Run all queries, not just SELECTs")
parser.add_option("--no-flush", dest="noflush", action="store_true", default=False, help="Do not flush query cache between each query")
parser.add_option("--slow", dest="slow", action="store", default=1, help="Slow query (float seconds) gets highlighted")
parser.add_option("--sort-time", dest="sorttime", action="store_true", default=False, help="Sort queries by execution time")
parser.add_option("--help", dest="help", action="store_true", default="", help="Show this help message.")

(options, args) = parser.parse_args()

if options.help or not len(args) == 2:
	parser.print_help()
	sys.exit(0)

options.session_id = args.pop()
options.database = args.pop()
options.slow = float(options.slow)

re_datetime = re.compile('^[0-9]{6} [ 0-9]{2}:[0-9]{2}:[0-9]{2}')

command_types = ['Quit', 'Connect', 'Init DB', 'Query', 'Statistics']

commands = []

if options.verbose:
	sys.stderr.write("Reading query log..\n")

try:
	f = file(options.logfile, 'r')
except IOError, e:
	sys.stderr.write(str(e)+"\n")
	sys.exit(1)

if options.verbose:
	sys.stderr.write("Searching for session %s..\n" % (options.session_id))

command = {}
for line in f:
	line = line.expandtabs()

	s_time = line[0:15]
	s_id = line[17:23].strip()
	s_command = line[24:35].strip()
	s_argument = line[36:]
	
	if s_command not in command_types:
		command['argument'] = command.get('argument', '') + line.lstrip()
	else:
		if s_id == options.session_id and command['command'] == 'Query':
			commands.append(command)
		command = {
			'time': s_time,
			'id': s_id,
			'command': s_command,
			'argument': s_argument
		}

if options.verbose:
	sys.stderr.write("Connecting to database to perform playback..\n")
try_pass = False
while True:
	if try_pass:
		options.password = getpass.getpass('Password: ', stream=sys.stderr)
	try:
		db = MySQLdb.connect(host=options.hostname, user=options.username, passwd=options.password,db=options.database)
	except MySQLdb.OperationalError, e:
		if e[0] == 1045:
			try_pass = True
			continue
		else:
			sys.stderr.write(str(e)+"\n")
			sys.exit(1)
	break

cursor = db.cursor()

total_time = 0
for command in commands:
	if command['command'] == 'Query' and (
		command['argument'].lstrip().upper().startswith('SELECT') or 
		options.all):

		if not options.noflush:
			cursor.execute('RESET QUERY CACHE')
		if options.verbose:
			sys.stderr.write('.')
		try:
			t_start = time.time()
			cursor.execute(command['argument'])
			t = time.time() - t_start
			total_time += t
			command['exec_time'] = t
			command['total_time'] = total_time
		except MySQLdb.OperationalError, e:
			command['error'] = str(e)
			command['exec_time'] = 0
			command['total_time'] = 0
	else:
		# For non-SELECT queries
		command['exec_time'] = -1
		command['total_time'] = 0

if options.verbose:
	sys.stderr.write("\n")

if options.sorttime:
	commands.sort(lambda a, b: cmp(a['exec_time'], b['exec_time']))

print """<html>
	<head>
		<style>
			body {
				font-family: helvetica;
			}
			th {
				background-color: #303030;
				color: #FFFFFF;
				font-size: 12px;
				border-bottom: 1px solid #505050;
			}
			td {
				border-bottom: 1px solid #505050;
			}
		</style>
	</head>
	<body>
		<table>
			<tr><th>Time (s)</th><th>Time so far (s)<th>Query</th>"""
for command in commands:
	if command['command'] == 'Query':
		error = ''
		if 'error' in command:
			error = "<br/>Error: <font color='#FF0000'>%s</font>" % (command['error'])
		bgcolor = '#FFFFFF'
		if command['exec_time'] < 0:
			# Non-SELECT queries
			bgcolor='#909090'
		elif command['exec_time'] > options.slow:
			# Slow SELECT queries
			bgcolor='#FF3030';
		try:
			print "<tr bgcolor='%s' valign='top'><td><pre>%f</pre></td><td><pre>%f</pre></td><td><pre>%s</pre>%s</td></tr>" % (bgcolor, command['exec_time'], command['total_time'], command['argument'], error)
		except Exception, e:
			print "<tr><td>&nbsp;</td><td>%s</td></tr>" % (str(e))
print """
		</table>
		<table>
			<tr><th>Total exeuction time:</th><td>%f</td></tr>
		</table>
	</body>
	</html>
""" % (total_time)
