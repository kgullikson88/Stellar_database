#!/usr/bin/python

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation

from DatabaseConnection import DatabaseConnection


dbc = DatabaseConnection()

# ========================
# Define database classes
# ========================
Base = declarative_base(bind=dbc.engine)


class Journal(Base):
    __tablename__ = 'journal'
    __table_args__ = {'autoload': True}


class Reference(Base):
    __tablename__ = 'reference'
    __table_args__ = {'autoload': True}


class Author(Base):
    __tablename__ = 'author'
    __table_args__ = {'autoload': True}


class Reference_to_Author(Base):
    __tablename__ = 'reference_to_author'
    __table_args__ = {'autoload': True}


class Cluster(Base):
    __tablename__ = 'cluster'
    __table_args__ = {'autoload': True}


class Star(Base):
    __tablename__ = 'star'
    __table_args__ = {'autoload': True}


class Star_System(Base):
    __tablename__ = 'star_system'
    __table_args__ = {'autoload': True}

    def __contains__(self, star):
        """
        Check to see if the given star is in this system
        :param star:
        :return: bool (True if the star is in the system, False if not)
        """
        retval = False
        for s in self.stars:
            if s.name == star.name:
                retval = True
        return retval



class Star_to_Star_System(Base):
    __tablename__ = 'star_to_star_system'
    __table_args__ = {'autoload': True}


class Configuration(Base):
    __tablename__ = 'configuration'
    __table_args__ = {'autoload': True}

    def get_primary(self):
        return self.star_system1.stars


class Instrument(Base):
    __tablename__ = 'instrument'
    __table_args__ = {'autoload': True}


class Spectrum(Base):
    __tablename__ = 'spectrum'
    __table_args__ = {'autoload': True}


class CCF(Base):
    __tablename__ = 'ccf'
    __table_args__ = {'autoload': True}


class Observation(Base):
    __tablename__ = 'observation'
    __table_args__ = {'autoload': True}  # =========================


# Define relationships here
# =========================

# ####     Star relationships       #####
Star.temperature_ref = relation(Reference, foreign_keys=[Star.temperature_ref_id])
Star.logg_ref = relation(Reference, foreign_keys=[Star.logg_ref_id])
Star.metallicity_ref = relation(Reference, foreign_keys=[Star.metallicity_ref_id])
Star.mass_ref = relation(Reference, foreign_keys=[Star.mass_ref_id])
Star.radius_ref = relation(Reference, foreign_keys=[Star.radius_ref_id])
Star.spectral_type_ref = relation(Reference, foreign_keys=[Star.spectral_type_ref_id])
Star.vsini_ref = relation(Reference, foreign_keys=[Star.vsini_ref_id])
Star.vsys_ref = relation(Reference, foreign_keys=[Star.vsys_ref_id])
Star.parallax_ref = relation(Reference, foreign_keys=[Star.parallax_ref_id])
Star.Vmag_ref = relation(Reference, foreign_keys=[Star.Vmag_ref_id])
Star.Kmag_ref = relation(Reference, foreign_keys=[Star.Kmag_ref_id])
Star.cluster = relation(Cluster, backref='stars')
Star.systems = relation(Star_System, secondary=Star_to_Star_System.__table__, backref='stars')

#####     Reference relationships       #####
Reference.journal = relation(Journal)
Reference.authors = relation(Author, secondary=Reference_to_Author.__table__, backref='journals')

# ####     Cluster relationships         #####
Cluster.reference = relation(Reference)

#####     Star system relationships       #####
#Star_System.configurations = relation(Configuration, foreign_keys=[Configuration])

#####     Configuration relationships       #####
Configuration.primary = relation(Star_System, foreign_keys=[Configuration.star_system1_id], backref='primaries')
Configuration.secondary = relation(Star_System, foreign_keys=[Configuration.star_system2_id], backref='secondaries')

#####     Observation relationships       #####
Observation.star = relation(Star, backref='observations')
Observation.instrument = relation(Instrument, backref='observations')
Observation.spectrum = relation(Spectrum, backref='observation')
Observation.ccf = relation(CCF, backref='observation')

#####     Instrument relationships       #####
Instrument.reference = relation(Reference)
