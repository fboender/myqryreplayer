MyQryReplayer
=============

About
-----

MyQryReplayer is a tool which can read the MySQL query log and replay an
entire session's worth of queries against a database (SELECT queries
only by default). While doing so, it records the time each query took to
run, and any queries that failed including their error messages.
MyQryReplayer can be used to inspect query performance, and to check a
log of queries against a database for possible errors (when upgrading to
a new version of MySQL for example).

Usage
-----

MyQryReplayer uses the MySQL query log as its input. You can enable the
query log in MySQL by opening the my.cnf file (usually in
/etc/mysql/my.cnf) and look for the '[mysqld]' section. In it, set the
'log' variable to a file:

	#
	# * Logging and Replication
	#
	# Both location gets rotated by the cronjob.
	# Be aware that this log type is a performance killer.
	log		= /var/log/mysql/mysql.log

MySQL will now log all commands (including all queries) sent to the
database to the '/var/log/mysql/mysql.log' file. Commands are grouped by
session. Each session runs from the first connect to the database until
the client disconnects again. 

You can now run MyQryReplayer like this:

./myqryreplayer.py -u user -h localhost ems2devlocal 554 > out.html

This will use the default log location '/var/log/mysql/mysql.log' (use
-l option if log is somewhere else), scan it for all commands sent to
the database during session '554'. It will then connect to the MySQL
server at localhost, using username 'user'. If 'user' requires a
password, MyQryReplayer will automatically ask for it. You can also
specify a password on the commandline using the -p option.
MyQryReplayer's output is a HTML document containing the replay
information. In the case above it is redirected to a file named
'out.html'.

Full usage:

Usage: ./myqryreplayer.py [option] <DATABASE> <SESSION_ID>

Options:
  -V, --verbose         Show more output
  -l LOGFILE, --logfile=LOGFILE
                        Path to the MySQL query log file
  -u USERNAME           MySQL Username
  -h HOSTNAME, --hostname=HOSTNAME
                        MySQL Hostname
  -p PASSWORD           MySQL Password
  --all                 Run all queries, not just SELECTs
  --no-flush            Do not flush query cache between each query
  --slow=SLOW           Slow query (float seconds) gets highlighted
  --sort-time           Sort queries by execution time
  --help                Show this help message.

Operation
---------

MyQryReplayer runs queries and collects results in the following:

  - Query execution time measured is only the time it took the MySQL
	server to execute the query. The results are not retrieved.
  - Total execution time is the sum of all query execution times so far,
	not real wall-time.
  - Between executing each query, MyQryReplayer will reset the query
	cache. Use --no-flush to disable this.

Output
------

MyQryReplayer outputs a HTML document containing the results of the
replaying:

  - By default, only SELECT statements are executed (use --all for all)
  - Per query, the time to execute the query is measured.
  - Per query, the total time so far of all queries is measured.
  - Slow queries (2 seconds by default) will get a redish background
	color)
  - Queries not ran (UPDATE/DELETE/INSERT if --all is not specified)
	will still be listed, but they well appear grey, and their times
	will be 0.

Copyright
---------

MyQryReplayer is written by Ferry Boender.

(C) Copyright 2009, Ferry Boender

Released under the MIT license. See LICENSE for the full license.
