#!/usr/bin/python

"""
  This script queries the database, to find all the students that belong to each supervisor.
  It then checks which clubs each student belongs to, and lists all clubs the all the students a supervisor 'owns'
    belong to.
"""

import sys
import sqlalchemy
from SQLiteConnection import engine, Session
from ModelClasses import *

filename = 'student_data.txt'

infile = open(filename)

session = Session()

supervisors = session.query(Supervisor).all()
for supervisor in supervisors:
    print '{} {} (Room {})'.format(supervisor.first_name, supervisor.last_name, supervisor.room_number)
    club_names = []
    for student in supervisor.students:
        #print '\t{} {}'.format(student.first_name, student.last_name)
        for club in student.clubs:
            if club.name not in club_names:
                club_names.append(club.name)
    for name in club_names:
        print '\t{}'.format(name)