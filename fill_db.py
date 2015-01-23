#!/usr/bin/python
from __future__ import print_function

import logging
import os

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
        data = output[0]
        if len(data) > 1:
            logging.warn('Multiple matches for star {} in Pastel catalog. Using the first one!'.format(starname))
            data.remove_rows(range(1, len(data)))

        bibcode = data['bibcode'].item().strip()
        ref, self.sql_session = get_reference(self.sql_session, bibcode if len(bibcode) > 0 else 'Unknown')
        print(data)
        print(ref)
        if not data['Teff'].mask:
            star.temperature = data['Teff'].item()
            print(bibcode)
            star.temperature_ref = ref
        if not data['e_Teff'].mask:
            star.temperature_error = data['e_Teff'].item()
        if not data['logg'].mask:
            star.logg = data['logg'].item()
            star.logg_ref = ref
        if not data['e_logg'].mask:
            star.logg_error = data['e_logg'].item()
        if not data['__Fe_H_'].mask:
            star.metallicity = data['__Fe_H_'].item()
            star.metallicity_ref = ref
        if not data['e__Fe_H_'].mask:
            star.metallicity_error = data['e__Fe_H_'].item()

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



class Multiplicity():
    def __init__(self, csv_dir='{}/Dropbox/School/Research/Databases/A_star/Multiplicity/'.format(os.environ['HOME'])):
        self.sb9 = pd.read_csv('{}SB9_WithNames.txt'.format(csv_dir), sep='|')
        self.wds = pd.read_csv('{}WDS_WithNames.txt'.format(csv_dir), sep='|')
        self.vast = pd.read_csv('{}VAST_WithNames.txt'.format(csv_dir), sep='|')
        self.et08 = pd.read_csv('{}ET2008_WithNames.txt'.format(csv_dir), sep='|')

        # Convert the DEC to the appropriate format in WDS
        self.wds = self.wds.dropna(subset=['RA', 'DEC'])
        self.wds['DEC'] = self.wds['DEC'].map(lambda s: HelperFunctions.convert_hex_string(s, delimiter=' '))

    def check_multiplicity(self, db_session, d=1.0):
        """
        Cross-references the database stars against the multiplicity databases
        :param db_session: a sqlalchemy session instance
        :keyword d: The on-sky distance between the database star and the entry in the multiplicity databases (in arcsec)
        """
        d /= 3600.0  #Convert d to degrees
        for star in db_session.query(Star).all():
            print(star.name)
            ra = star.RA * 15.0
            dec = star.DEC
            sb9 = self.sb9.loc[((self.sb9.RA - ra)**2 < d) & ((self.sb9.DEC - dec)**2 < d)].drop_duplicates()
            wds = self.wds.loc[((self.wds.RA - ra)**2 < d) & ((self.wds.DEC - dec)**2 < d)].drop_duplicates()
            vast = self.vast.loc[((self.vast.RA - ra)**2 < d) & ((self.vast.DEC - dec)**2 < d)].drop_duplicates()
            et08 = self.et08.loc[((self.et08.RA - ra)**2 < d) & ((self.et08.DEC - dec)**2 < d)].drop_duplicates()

            if len(sb9) > 0:
                self.parse_sb9(sb9, star)
            if len(wds) > 0:
                self.parse_wds(wds, star)
            if len(vast) > 0:
                self.parse_vast(vast, star)
            if len(et08) > 0:
                self.parse_et08(et08, star)


    def parse_sb9(self, df, star):
        """
        Pull the information I am interested in out of the SB9 catalog
        """
        cols = [u'Sp1', u'Sp2', u'Per', u'e_Per', u'K1', u'e_K1', u'K2', u'e_K2']
        info  = df[cols]
        info['Separation'] = 0.0  # Basically 0 if it has a spectroscopic orbit

        return info

    def parse_wds(self, df, star):
        """
        Pull the relevant information from the wds catalog
        """
        cols = ['sep2', 'mag1', 'mag2', 'RefCode', 'Disc']
        info = df[cols]
        return info

    def parse_vast(self, df, star):
        print(df.keys())
        cols = ['Age', 'AgeRef', 'Mass1', 'Mass2', 'MagDiff', 'Band', 'Separation']
        info = df[cols]
        return info

    def parse_et08(self, df, star):
        print(df.keys())
        print(df)
        cols = ['Conf', 'Cluster', 'BibCode']
        info = df[cols]
        info = info.drop_duplicates()

        # Parse the configuration
        outfile = open('configurations.txt', 'a')
        vals = info['Conf'].values
        for val in vals:
            outfile.write(val.strip() + '\n')
        outfile.close()
        return info





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

        test_aq = lambda key, default=None: star[key].item() if not star[key].mask else default
        name = test_aq('MAIN_ID')
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
        rv = test_aq('RVZ_RADVEL')
        e_rv = test_aq('RVZ_ERROR')
        rv_type = test_aq('RVZ_TYPE')
        bib_rv = test_aq('RVZ_BIBCODE', default='')
        if 'z' in rv_type:
            rv /= constants.c.cgs.to(u.km/u.sec).value
            e_rv /= constants.c.cgs.to(u.km/u.sec).value

        # Get the necessary reference objects
        Vmag_ref, session = get_reference(session, bib_Vmag if len(bib_Vmag.strip()) > 0 else 'Unknown')
        Kmag_ref, session = get_reference(session, bib_Kmag if len(bib_Kmag.strip()) > 0 else 'Unknown')
        plx_ref, session = get_reference(session, bib_plx if len(bib_plx.strip()) > 0 else 'Unknown')
        spt_ref, session = get_reference(session, bib_spt if len(bib_spt.strip()) > 0 else 'Unknown')
        rv_ref, session = get_reference(session, bib_rv if len(bib_rv.strip()) > 0 else 'Unknown')
        vsini_ref, session = get_reference(session, bib_vsini if len(bib_vsini.strip()) > 0 else 'Unknown')

        # Add the data to the database
        try:
            entry = session.query(Star).filter(Star.name == name).one()
            print('Star ({}) already in database! Skipping...'.format(starname))
        except sqlalchemy.orm.exc.NoResultFound:
            entry = Star()
            entry.name = None if (isinstance(name, str) and name.strip() == '') else name
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
            entry.vsys = None if (isinstance(rv, str) and rv.strip() == '') else rv
            entry.vsys_error = None if (isinstance(e_rv, str) and e_rv.strip() == '') else e_rv
            entry.vsys_ref = rv_ref

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
    #session = add_stellar_parameters(session)

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
