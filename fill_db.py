#!/usr/bin/python
from __future__ import print_function

import logging
import os
import re
import sys

import numpy as np
import sqlalchemy
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
from astropy import units as u
from astropy import constants
import HelperFunctions
import pandas as pd
import SpectralTypeRelations

from SQLiteConnection import engine, Session
from ModelClasses import *


MS = SpectralTypeRelations.MainSequence()

def get_reference(session, bibcode):
    """
    Return a reference object for the specified bibcode
    """
    try:
        entry = session.query(Reference).filter(Reference.bibcode == bibcode).one()
    except sqlalchemy.orm.exc.NoResultFound:
        entry = Reference()
        entry.bibcode = bibcode
        session.add(entry)
        session.flush()

        #TODO: get author name, journal, volume, page, and year
    return entry, session


class StellarParameter():
    def __init__(self, sql_session):
        self.pastel = Vizier(columns=['_RAJ2000', 'DEJ2000', 'ID', 'Teff', 'e_Teff',
                                      'logg', 'e_logg', '[Fe/H]', 'e_[Fe/H]', 'bibcode'],
                             catalog='B/pastel/pastel')
        self.pastel_bibcode = '2010A&A...515A.111S'
        self.sql_session = sql_session

    def get_pastel_pars(self, starname):
        """
        Get stellar parameters from the pastel catalog for the given star, and put them in the database
        :param starname: the name (main id) of the star, as it appears in the database!
        :return: bool (False if failed, True if success)
        """
        try:
            star = self.sql_session.query(Star).filter(Star.name == starname).one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise ValueError('Must put star in database before giving it parameters!')

        output = self.pastel.query_object(starname)
        if len(output) == 0:
            logging.warn('No match for star {} in Pastel catalog'.format(starname))
            return False
        data = output[0].to_pandas()
        if len(data) > 1:
            logging.info('Multiple matches for star {} in Pastel catalog. Using the mean values'.format(starname))

        # Assign default values for the uncertainties
        data.loc[data.e_Teff.isnull(), 'e_Teff'] = 200
        data.loc[data.e_logg.isnull(), 'e_logg'] = 0.5
        data.loc[data['e__Fe_H_'].isnull(), 'e__Fe_H_'] = 0.5

        # Drop duplicated values
        data.drop_duplicates(subset='bibcode', inplace=True)
        print(data)

        # Get the values from the table
        Teff_mask = data.Teff.notnull()
        Teff_arr = data.loc[Teff_mask, 'Teff'].values
        e_Teff_arr = data.loc[Teff_mask, 'e_Teff'].values
        logg_mask = data.logg.notnull()
        logg_arr = data.loc[logg_mask, 'logg'].values
        e_logg_arr = data.loc[logg_mask, 'e_logg'].values
        feh_mask = data['__Fe_H_'].notnull()
        feh_arr = data.loc[feh_mask, '__Fe_H_'].values
        e_feh_arr = data.loc[feh_mask, 'e__Fe_H_'].values


        # Get the error-weighted mean values
        Teff, e_Teff = HelperFunctions.weighted_mean_and_stddev(Teff_arr, 
                                                                weights=1.0/e_Teff_arr**2,
                                                                bad_value=None)
        logg, e_logg = HelperFunctions.weighted_mean_and_stddev(logg_arr, 
                                                                weights=1.0/e_logg_arr**2,
                                                                bad_value=None)
        feh, e_feh = HelperFunctions.weighted_mean_and_stddev(feh_arr, 
                                                              weights=1.0/e_feh_arr**2,
                                                              bad_value=None)
        print(Teff, e_Teff)
        print(logg, e_logg)
        print(feh, e_feh)

        # Get the reference to the pastel reference table
        bibcode = self.pastel_bibcode
        ref, self.sql_session = get_reference(self.sql_session, bibcode if len(bibcode) > 0 else 'Unknown')

        # Put the data into the database
        star.temperature = Teff
        star.temperature_error = e_Teff
        star.temperature_ref = ref
        star.logg = logg
        star.logg_error = e_logg
        star.logg_ref = ref
        star.metallicity = feh
        star.metallicity_error = e_feh
        star.metallicity_ref = ref

        return True


    def get_all_pars(self):
        """
          Fill all the parameters from known catalogs
        """
        success = []
        fail = []
        for star in self.sql_session.query(Star).all():
            print(star.name)
            out = self.get_pastel_pars(star.name)
            if out:
                success.append(out)
            else:
                fail.append(out)
        logging.info('Of all stars in the database, we got stellar parameters for {} of them'.format(len(success)))
        return


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
                           'plx', 'plx_error', 'plx_bibcode')

    # loop over the files
    for starname in starlist:
        # Get data from the Simbad database
        star = sim.query_object(starname)
        print(starname)

        test_aq = lambda key, default=None: star[key].item() if not star[key].mask else default
        name = test_aq('MAIN_ID')
        #name = starname
        ra = HelperFunctions.convert_hex_string(star['RA'].item(), delimiter=' ')
        dec = HelperFunctions.convert_hex_string(star['DEC'].item(), delimiter=' ')
        Vmag = test_aq('FLUX_V')
        e_Vmag = test_aq('FLUX_ERROR_V')
        bib_Vmag = test_aq('FLUX_BIBCODE_V', default='')
        Kmag = test_aq('FLUX_K')
        e_Kmag = test_aq('FLUX_ERROR_K')
        bib_Kmag = test_aq('FLUX_BIBCODE_K', default='')
        plx = test_aq('PLX_VALUE')
        e_plx = test_aq('PLX_ERROR')
        bib_plx = test_aq('PLX_BIBCODE', default='')
        vsini = test_aq('ROT_Vsini')
        e_vsini = test_aq('ROT_err')
        bib_vsini = test_aq('ROT_bibcode', default='')
        spt = test_aq('SP_TYPE')
        bib_spt = test_aq('SP_BIBCODE', default='')
        

        # Get the necessary reference objects
        Vmag_ref, session = get_reference(session, bib_Vmag if len(bib_Vmag.strip()) > 0 else 'Unknown')
        Kmag_ref, session = get_reference(session, bib_Kmag if len(bib_Kmag.strip()) > 0 else 'Unknown')
        plx_ref, session = get_reference(session, bib_plx if len(bib_plx.strip()) > 0 else 'Unknown')
        spt_ref, session = get_reference(session, bib_spt if len(bib_spt.strip()) > 0 else 'Unknown')
        vsini_ref, session = get_reference(session, bib_vsini if len(bib_vsini.strip()) > 0 else 'Unknown')

        # Add the data to the database
        try:
            entry = session.query(Star).filter(Star.name == name).one()
            print('Star ({}) already in database! Skipping...'.format(starname))
        except sqlalchemy.orm.exc.NoResultFound:
            entry = Star()
            entry.name = starname
            entry.main_id = None if (isinstance(name, str) and name.strip() == '') else name
            entry.RA = None if (isinstance(ra, str) and ra.strip() == '') else ra
            entry.DEC = None if (isinstance(dec, str) and dec.strip() == '') else dec
            entry.Vmag = None if (isinstance(Vmag, str) and Vmag.strip() == '') else Vmag
            entry.Vmag_error = None if (isinstance(e_Vmag, str) and e_Vmag.strip() == '') else e_Vmag
            entry.Vmag_ref = Vmag_ref
            entry.Kmag = None if (isinstance(Kmag, str) and Kmag.strip() == '') else Kmag
            entry.Kmag_error = None if (isinstance(e_Kmag, str) and e_Kmag.strip() == '') else e_Kmag
            entry.Kmag_ref = Kmag_ref
            entry.parallax = None if (isinstance(plx, str) and plx.strip() == '') else plx
            entry.parallax_error = None if (isinstance(e_plx, str) and e_plx.strip() == '') else e_plx
            entry.parallax_ref = plx_ref
            entry.vsini = None if (isinstance(vsini, str) and vsini.strip() == '') else vsini
            entry.vsini_error = None if (isinstance(e_vsini, str) and e_vsini.strip() == '') else e_vsini
            entry.vsini_ref = vsini_ref
            entry.spectral_type = None if (isinstance(spt, str) and spt.strip() == '') else spt
            entry.spectral_type_ref = spt_ref

            session.add(entry)
            session.flush()

    return session


def add_stellar_parameters(session):
    SP = StellarParameter(session)
    SP.get_all_pars()
    return SP.sql_session





if __name__ == '__main__':
    session = Session()
    session.begin()
    session = get_simbad_data(session)
    session = add_stellar_parameters(session)
    #session = make_star_systems(session)
    #add_multiplicity(session)

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
