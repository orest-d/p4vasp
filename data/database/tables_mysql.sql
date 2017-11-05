CREATE TABLE IF NOT EXISTS #USERINFO (
  id                          INTEGER AUTO_INCREMENT,
  user_uid                    VARCHAR(255),
  username                    VARCHAR(255),
  passwd                      VARCHAR(255),
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS #CALC (
  id                          INTEGER AUTO_INCREMENT,
  name                        VARCHAR(255),
  keywords                    VARCHAR(255),
  user_id                     INTEGER,
  program                     VARCHAR(255),
  version                     VARCHAR(255),
  subversion                  VARCHAR(255),
  platform                    VARCHAR(255),
  cdatetime                   VARCHAR(255),
  path                        VARCHAR(255),
  free_energy                 DOUBLE,
  fermi_energy                DOUBLE,
  kpoints_text                TEXT,
  description                 TEXT,
  PRIMARY KEY (id)  
);

CREATE TABLE IF NOT EXISTS #PARAMETERS (
  calc_id                     INTEGER NOT NULL,
  name                        VARCHAR(255),
  fieldtype                   VARCHAR(255),
  isarray                     INTEGER,
  isspecified                 INTEGER,
  value                       VARCHAR(255),
  textvalue                   TEXT
);

CREATE TABLE IF NOT EXISTS #STRUCT (
  id                          INTEGER AUTO_INCREMENT,
  calc_id                     INTEGER,
  step                        INTEGER,
  scale                       DOUBLE,  
  comment                     VARCHAR(255),	 
  a11                         DOUBLE, 
  a12                         DOUBLE, 
  a13                         DOUBLE, 
  a21                         DOUBLE, 
  a22                         DOUBLE, 
  a23                         DOUBLE, 
  a31                         DOUBLE, 
  a32                         DOUBLE, 
  a33                         DOUBLE, 
  species                     INTEGER,
  PRIMARY KEY (id)  
);

CREATE TABLE IF NOT EXISTS #ENERGY (
  calc_id                     INTEGER,
  step                        INTEGER,
  energy                      DOUBLE
);

CREATE TABLE IF NOT EXISTS #STRUCTPOS (
  structure_id                INTEGER NOT NULL,
  calc_id                     INTEGER,
  atomnumber                  INTEGER,
  specie                      INTEGER,
  element                     VARCHAR(5),
  x                           DOUBLE,
  y                           DOUBLE,
  z                           DOUBLE
);

CREATE TABLE IF NOT EXISTS #STRUCTFORCE (
  structure_id                INTEGER NOT NULL,
  calc_id                     INTEGER,
  atomnumber                  INTEGER,
  x                           DOUBLE,
  y                           DOUBLE,
  z                           DOUBLE
);

CREATE TABLE IF NOT EXISTS #STRUCTVELOCITY (
  structure_id                INTEGER NOT NULL,
  calc_id                     INTEGER,
  atomnumber                  INTEGER,
  x                           DOUBLE,
  y                           DOUBLE,
  z                           DOUBLE
);

CREATE TABLE IF NOT EXISTS #STRUCTCONSTRAINTS (
  structure_id                INTEGER NOT NULL,
  calc_id                     INTEGER,
  atomnumber                  INTEGER,
  x                           BOOLEAN,
  y                           BOOLEAN,
  z                           BOOLEAN
);

CREATE TABLE IF NOT EXISTS #DOS (
  calc_id                     INTEGER,
  spin                        INTEGER,
  energy                      DOUBLE,
  density                     DOUBLE,
  integrated                  DOUBLE
);

CREATE TABLE IF NOT EXISTS #LDOS (
  calc_id                     INTEGER,
  spin                        INTEGER,
  energy                      DOUBLE,
  atomnumber                  INTEGER,
  orbital                     VARCHAR(6),
  density                     DOUBLE
);
