DROP TABLE IF EXISTS "journal";
CREATE TABLE "journal" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "name" TEXT);

DROP TABLE IF EXISTS "reference";
CREATE TABLE "reference" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE, "journal_id" INTEGER, "volume" INTEGER, "year" INTEGER, "page" INTEGER, "bibcode" TEXT, FOREIGN KEY (journal_id) REFERENCES journal (id));

DROP TABLE IF EXISTS "author";
CREATE TABLE "author" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, "first_name" TEXT, "last_name" TEXT);

DROP TABLE IF EXISTS "reference_to_author";
CREATE TABLE "reference_to_author" ("reference_id" INTEGER NOT NULL, "author_id" INTEGER NOT NULL, PRIMARY KEY ("reference_id", "author_id")
                                    FOREIGN KEY (reference_id) REFERENCES reference (id), FOREIGN KEY (author_id) REFERENCES author (id));


DROP TABLE IF EXISTS "cluster";
CREATE TABLE "cluster" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "name" TEXT, "age" FLOAT, "age_error" FLOAT, "distance" FLOAT, "distance_error" FLOAT, "RA" FLOAT, "DEC" FLOAT, "reference_id" INTEGER, FOREIGN KEY (reference_id) REFERENCES reference (id));

DROP TABLE IF EXISTS "star";
CREATE TABLE "star" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE, "name" TEXT , "cluster_id" INTEGER,
                     "spectral_type" TEXT, "spectral_type_ref_id" INTEGER, 
                     "temperature" FLOAT, "temperature_error" FLOAT, "temperature_ref_id" INTEGER, 
                     "logg" FLOAT, "logg_error" FLOAT, "logg_ref_id" INTEGER, 
                     "mass" FLOAT, "mass_error" FLOAT, "mass_ref_id" INTEGER, 
                     "metallicity" FLOAT, "metallicity_error" FLOAT, "metallicity_ref_id" INTEGER, 
                     "radius" FLOAT, "radius_error" FLOAT, "radius_ref_id" INTEGER, 
                     "vsini" FLOAT, "vsini_error" FLOAT, "vsini_ref_id" INTEGER, 
                     "vsys" FLOAT, "vsys_error" FLOAT, "vsys_ref_id" INTEGER,
                     "parallax" FLOAT, "parallax_error" FLOAT, "parallax_ref_id" INTEGER, 
                     "Vmag" FLOAT, "Vmag_error" FLOAT, "Vmag_ref_id" INTEGER, 
                     "Kmag" FLOAT, "Kmag_error" FLOAT, "Kmag_ref_id" INTEGER, 
                     "RA" FLOAT, "DEC" FLOAT,
                    FOREIGN KEY (temperature_ref_id) REFERENCES reference (id), 
                    FOREIGN KEY (logg_ref_id) REFERENCES reference (id), 
                    FOREIGN KEY (mass_ref_id) REFERENCES reference (id), 
                    FOREIGN KEY (metallicity_ref_id) REFERENCES reference (id), 
                    FOREIGN KEY (spectral_type_ref_id) REFERENCES reference (id), 
                    FOREIGN KEY (radius_ref_id) REFERENCES reference (id), 
                    FOREIGN KEY (vsini_ref_id) REFERENCES reference (id), 
                    FOREIGN KEY (vsys_ref_id) REFERENCES reference (id), 
                    FOREIGN KEY (parallax_ref_id) REFERENCES reference (id), 
                    FOREIGN KEY (Vmag_ref_id) REFERENCES reference (id), 
                    FOREIGN KEY (Kmag_ref_id) REFERENCES reference (id),
                    FOREIGN KEY (cluster_id) REFERENCES cluster (id));

DROP TABLE IF EXISTS "star_system";
CREATE TABLE "star_system" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE);

DROP TABLE IF EXISTS "star_to_star_system";
CREATE TABLE "star_to_star_system" ("star1_id" INTEGER NOT NULL, "star2_id" INTEGER NOT NULL, "star_system_id" INTEGER NOT NULL,
                                    "separation" FLOAT, "separation_error" FLOAT, "separation_ref_id" INTEGER, "period" FLOAT,
                                    "period_error" FLOAT, "spec_ref_id" INTEGER, "component" TEXT,
                                    "K1" FLOAT, "K1_error" FLOAT, "K2" FLOAT, "K2_error" FLOAT,
                                    PRIMARY KEY ("star1_id", "star2_id", "star_system_id")
                                    FOREIGN KEY (star1_id) REFERENCES star (id),
                                    FOREIGN KEY (star2_id) REFERENCES star (id),
                                    FOREIGN KEY (star_system_id) REFERENCES star_system (id),
                                    FOREIGN KEY (separation_ref_id) REFERENCES reference (id),
                                    FOREIGN KEY (spec_ref_id) REFERENCES reference (id));

DROP TABLE IF EXISTS "instrument";
CREATE TABLE "instrument" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "name" TEXT, "reference_id" INTEGER, FOREIGN KEY (reference_id) REFERENCES reference (id));

DROP TABLE IF EXISTS "spectrum";
CREATE TABLE "spectrum" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "filename" TEXT, "snr" FLOAT, "exposure" FLOAT);

DROP TABLE IF EXISTS "ccf";
CREATE TABLE "ccf" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "directory" TEXT, "peak_temperature" FLOAT, "peak_metal" FLOAT, "peak_vsini" FLOAT, "peak_rv" FLOAT, "peak_significance" FLOAT);

DROP TABLE IF EXISTS "observation";
CREATE TABLE "observation" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE , "instrument_id" INTEGER, "date" TEXT, "star_id" INTEGER, "spectrum_id" INTEGER, "ccf_id" INTEGER, "notes" TEXT, FOREIGN KEY (instrument_id) REFERENCES instrument (id), FOREIGN KEY (star_id) REFERENCES star (id), FOREIGN KEY (spectrum_id) REFERENCES spectrum (id), FOREIGN KEY (ccf_id) REFERENCES ccf (id));
