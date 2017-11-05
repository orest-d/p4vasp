CREATE TABLE IF NOT EXISTS #USERINFO (
  id                          INTEGER PRIMARY KEY AUTOINCREMENT,
  user_uid                    VARCHAR(255),
  username                    VARCHAR(255),
  passwd                      VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS #CALC (
  id                          INTEGER PRIMARY KEY AUTOINCREMENT,
  name                        VARCHAR(255),
  keywords                    VARCHAR(255),
  user_id                     INTEGER,
  program                     VARCHAR(255),
  version                     VARCHAR(255),
  subversion                  VARCHAR(255),
  platform                    VARCHAR(255),
  cdatetime                   VARCHAR(255),
  path                        VARCHAR(255),
  free_energy                 REAL,
  fermi_energy                REAL,
  kpoints_text                TEXT,
  description                 TEXT
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
  id                          INTEGER PRIMARY KEY AUTOINCREMENT,
  calc_id                     INTEGER,
  step                        INTEGER,
  scale                       REAL,  
  comment                     VARCHAR(255),	 
  a11                         REAL, 
  a12                         REAL, 
  a13                         REAL, 
  a21                         REAL, 
  a22                         REAL, 
  a23                         REAL, 
  a31                         REAL, 
  a32                         REAL, 
  a33                         REAL, 
  species                     INTEGER
);

CREATE TABLE IF NOT EXISTS #ENERGY (
  calc_id                     INTEGER,
  step                        INTEGER,
  energy                      REAL
);

CREATE TABLE IF NOT EXISTS #STRUCTPOS (
  structure_id                INTEGER NOT NULL,
  calc_id                     INTEGER,
  atomnumber                  INTEGER,
  specie                      INTEGER,
  element                     VARCHAR(5),
  x                           REAL,
  y                           REAL,
  z                           REAL
);

CREATE TABLE IF NOT EXISTS #STRUCTFORCE (
  structure_id                INTEGER NOT NULL,
  calc_id                     INTEGER,
  atomnumber                  INTEGER,
  x                           REAL,
  y                           REAL,
  z                           REAL
);

CREATE TABLE IF NOT EXISTS #STRUCTVELOCITY (
  structure_id                INTEGER NOT NULL,
  calc_id                     INTEGER,
  atomnumber                  INTEGER,
  x                           REAL,
  y                           REAL,
  z                           REAL
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
  energy                      REAL,
  density                     REAL,
  integrated                  REAL
);

CREATE TABLE IF NOT EXISTS #LDOS (
  calc_id                     INTEGER,
  spin                        INTEGER,
  energy                      REAL,
  atomnumber                  INTEGER,
  orbital                     VARCHAR(6),
  density                     REAL
);
