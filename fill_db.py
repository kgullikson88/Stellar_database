#!/usr/bin/python
from __future__ import print_function

import sqlalchemy
from astroquery.simbad import Simbad
from astropy import units as u
from astropy import constants
import HelperFunctions

from SQLiteConnection import engine, Session
from ModelClasses import *


def get_reference(session, bibcode):
    """
    Return a reference object for the specified bibcode
    """
    # entry = session.query(Reference).filter(Reference.bibcode == bibcode).one()
    try:
        entry = session.query(Reference).filter(Reference.bibcode == bibcode).one()
    except sqlalchemy.orm.exc.NoResultFound:
        entry = Reference()
        entry.bibcode = bibcode
        session.add(entry)

        #TODO: get author name, journal, volume, page, and year
    return entry, session


def get_simbad_data(session, starlist_filename='starlist.dat'):
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
                           'rvel', 'rvz_bibcode', 'rvz_error', 'rvz_radvel', 'rvz_type')

    # loop over the files
    for starname in starlist:
        # Get data from the Simbad database
        star = sim.query_object(starname)
        print(starname)
        # print star.keys()
        name = star['MAIN_ID'].item()
        ra = HelperFunctions.convert_hex_string(star['RA'].item(), delimiter=' ')
        dec = HelperFunctions.convert_hex_string(star['DEC'].item(), delimiter=' ')
        Vmag = star['FLUX_V'].item()
        e_Vmag = star['FLUX_ERROR_V'].item()
        bib_Vmag = star['FLUX_BIBCODE_V'].item()
        Kmag = star['FLUX_K'].item()
        e_Kmag = star['FLUX_ERROR_K'].item()
        bib_Kmag = star['FLUX_BIBCODE_K'].item()
        plx = star['PLX_VALUE'].item()
        e_plx = star['PLX_ERROR'].item()
        bib_plx = star['PLX_BIBCODE'].item()
        vsini = star['ROT_Vsini'].item()
        spt = star['SP_TYPE'].item()
        bib_spt = star['SP_BIBCODE'].item()
        rv = star['RVZ_RADVEL'].item()
        e_rv = star['RVZ_ERROR'].item()
        rv_type = star['RVZ_TYPE'].item()
        bib_rv = star['RVZ_BIBCODE'].item()
        if 'z' in rv_type:
            rv /= constants.c.cgs.to(u.km/u.sec).value
            e_rv /= constants.c.cgs.to(u.km/u.sec).value

        # Get the necessary reference objects
        print(bib_Vmag)
        Vmag_ref, session = get_reference(session, bib_Vmag if len(bib_Vmag.strip()) > 0 else 'Unknown')
        Kmag_ref, session = get_reference(session, bib_Kmag if len(bib_Kmag.strip()) > 0 else 'Unknown')
        plx_ref, session = get_reference(session, bib_plx if len(bib_plx.strip()) > 0 else 'Unknown')
        spt_ref, session = get_reference(session, bib_spt if len(bib_spt.strip()) > 0 else 'Unknown')
        rv_ref, session = get_reference(session, bib_rv if len(bib_rv.strip()) > 0 else 'Unknown')

        # Add the data to the database
        try:
            entry = session.query(Star).filter(Star.name == name).one()
        except sqlalchemy.orm.exc.NoResultFound:
            entry = Star()
            entry.name = name
            entry.RA = ra
            entry.DEC = dec
            entry.Vmag = Vmag
            entry.Vmag_error = e_Vmag
            entry.Vmag_ref = Vmag_ref
            entry.Kmag = Kmag
            entry.Kmag_error = e_Kmag
            entry.Kmag_ref = Kmag_ref
            entry.parallax = plx
            entry.parallax_error = e_plx
            entry.parallax_ref = plx_ref
            entry.vsini = vsini
            entry.spectral_type = spt
            entry.spectral_type_ref = spt_ref
            entry.vsys = rv
            entry.vsys_error = e_rv
            entry.vsys_ref = rv_ref

        session.add(entry)

    return session









if __name__ == '__main__':
    session = Session()
    session.begin()
    session = get_simbad_data(session)

    session.commit()
    engine.dispose()


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
