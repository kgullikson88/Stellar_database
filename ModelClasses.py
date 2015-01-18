#!/usr/bin/python

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation

from DatabaseConnection import DatabaseConnection

dbc = DatabaseConnection()

# ========================
# Define database classes
# ========================
Base = declarative_base(bind=dbc.engine)

class Star(Base):
	__tablename__ = 'star'
	__table_args__ = {'autoload' : True}

class Reference(Base):
	__tablename__ = 'reference'
	__table_args__ = {'autoload' : True}


class Author(Base):
    __tablename__ = 'author'
    __table_args__ = {'autoload': True}


class Reference_to_Author(Base):
    __tablename__ = 'reference_to_author'
    __table_args__ = {'autoload': True}


class Journal(Base):
	__tablename__ = 'journal'
	__table_args__ = {'autoload' : True}

class Cluster(Base):
	__tablename__ = 'cluster'
	__table_args__ = {'autoload' : True}

class Star_System(Base):
	__tablename__ = 'star_system'
	__table_args__ = {'autoload' : True}

class Observation(Base):
	__tablename__ = 'observation'
	__table_args__ = {'autoload' : True}

class Spectrum(Base):
	__tablename__ = 'spectrum'
	__table_args__ = {'autoload' : True}

class CCF(Base):
	__tablename__ = 'ccf'
	__table_args__ = {'autoload' : True}

class Instrument(Base):
	__tablename__ = 'instrument'
	__table_args__ = {'autoload' : True}


# =========================
# Define relationships here
# =========================

#####     Star relationships       #####
Star.temperature_ref = relation(Reference, backref='stars', foreign_keys=['temperature_ref_id'])
Star.logg_ref = relation(Reference, backref='stars', foreign_keys=['logg_ref_id'])
Star.metallicity_ref = relation(Reference, backref='stars', foreign_keys=['metallicity_ref_id'])
Star.mass_ref = relation(Reference, backref='stars', foreign_keys=['mass_ref_id'])
Star.radius_ref = relation(Reference, backref='stars', foreign_keys=['radius_ref_id'])
Star.spectral_type_ref = relation(Reference, backref='stars', foreign_keys=['spectral_type_ref_id'])
Star.vsini_ref = relation(Reference, backref='stars', foreign_keys=['vsini_ref_id'])
Star.vsys_ref = relation(Reference, backref='stars', foreign_keys=['vsys_ref_id'])
Star.parallax_ref = relation(Reference, backref='stars', foreign_keys=['parallax_ref_id'])
Star.Vmag_ref = relation(Reference, backref='stars', foreign_keys=['Vmag_ref_id'])
Star.Kmag_ref = relation(Reference, backref='stars', foreign_keys=['Kmag_ref_id'])
Star.cluster = relation(Cluster, backref='stars')

#####     Reference relationships       #####
Reference.journal = relation(Journal, backref='references')
Reference.authors = relation(Author, secondary=Reference_to_Author.__table__, backref='journals')

# ####     Cluster relationships         #####
Cluster.reference = relation(Reference)

#####     Star system relationships       #####
Star_System.primary = relation(Star, backref='star_systems', foreign_keys=['star1_id'])
Star_System.secondary = relation(Star, backref='star_systems', foreign_keys=['star2_id'])
Star_System.image_ref = relation(Reference, foreign_keys=['separation_ref_id'])
Star_System.spec_ref = relation(Reference, foreign_keys=['spec_ref_id'])

#####     Observation relationships       #####
Observation.star = relation(Star, backref='observations')
Observation.instrument = relation(Instrument, backref='observations')
Observation.spectrum = relation(Spectrum, backref='observation')
Observation.ccf = relation(CCF, backref='observation')

#####     Instrument relationships       #####
Instrument.reference = relation(Reference)
