#!/usr/bin/python

import sys
import sqlalchemy
from SQLiteConnection import engine, Session
from ModelClasses import *
from astroquery.simbad import Simbad

def fill_star_data(session, starlist_filename='starlist.dat'):
    # Read in the star list
    infile = open(starlist_filename)
    starlist = infile.readlines()
    infile.close()

    # Make an appropriate Simbad search object
    sim = Simbad()
    sim.add_votable_fields('flux(V)', 'flux_error(V)', 'flux_bibcode(V)',
                           'flux(K)', 'flux_error(K)', 'flux_bibcode(K)',
                           'rot',
                           'sp', 'sp_bibcode',
                           'plx', 'plx_error', 'plx_bibcode',
                           'rv_value', 'rvel', 'rvz_bibcode', 'rvz_error', 'rvz_radvel', 'rvz_type')




if __name__ == '__main__':
    session = Session()


""" ===========================================
# My code here!
=========================================== """

"""
filename = 'student_data.txt'

infile = open(filename)

lines = infile.readlines()
for line in lines[5:]:
    print '\n\n', line.strip()
    fields = line.split('|')

    # Make a student
    student = Student()
    student.first_name = fields[0].strip()
    student.last_name = fields[1].strip()
    print 'Adding student {} {}'.format(student.first_name, student.last_name)
    session.add(student)

    # Supervisors
    sups = [s.strip() for s in fields[3].split(',')]
    for sup in sups:
        if len(sup) == 0:
            print 'Empty supervisor!'
            continue
        last_name = sup.split('/')[0]
        room_number = int(sup.split()[-1])

        # Make the supervisor if necessary
        try:
            one_supervisor = session.query(Supervisor).filter(Supervisor.last_name == last_name).one()
        except sqlalchemy.orm.exc.NoResultFound:
            one_supervisor = Supervisor()
            one_supervisor.first_name = ''
            one_supervisor.last_name = last_name
            one_supervisor.room_number = room_number
            session.add(one_supervisor)
        except sqlalchemy.orm.exc.MultipleResultsFound:
            print 'There is more than one supervisor with the same name ({})!'.format(last_name)
            sys.exit(1)

        # Add the supervisor to this student
        print 'Adding supervisor {} {}'.format(one_supervisor.first_name, one_supervisor.last_name)
        student.supervisors.append(one_supervisor)


    # Clubs
    clubs = [c.strip() for c in fields[5].split(',')]
    for club_name in clubs:
        if len(club_name.strip()) == 0:
            print 'Empty club!'
            continue

        # Make the club if necessary
        try:
            one_club = session.query(Club).filter(Club.name == club_name).one()
        except sqlalchemy.orm.exc.NoResultFound:
            one_club = Club()
            one_club.name = club_name
            session.add(one_club)
        except sqlalchemy.orm.exc.MultipleResultsFound:
            print 'There is more than one club with the same name ({})!'.format(club_name)
            sys.exit(1)

        # Add the club to this student
        print 'Adding {} club'.format(one_club.name)
        student.clubs.append(one_club)

    # Status
    stat = fields[4].strip()
    try:
        status = session.query(Status).filter(Status.label == stat).one()
    except sqlalchemy.orm.exc.NoResultFound:
        status = Status()
        status.label = stat
        session.add(status)
    except sqlalchemy.orm.exc.MultipleResultsFound:
        print 'There is more than one status with the same name ({})!'.format(stat)
        sys.exit(1)

    print 'Adding status {}'.format(status.label)
    student.status = status

    # City
    student_city = fields[2].strip()
    try:
        city = session.query(City).filter(City.name == student_city).one()
    except sqlalchemy.orm.exc.NoResultFound:
        city = City()
        city.name = student_city
        session.add(city)
    except sqlalchemy.orm.exc.MultipleResultsFound:
        print 'There is more than one city with the same name ({})!'.format(stat)
        sys.exit(1)

    print 'Adding city {}'.format(city.name)
    student.city = city
"""

""" ===========================================
# End my code!
=========================================== """

session.commit()

engine.dispose()
sys.exit(0)