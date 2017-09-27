CREATE TABLE
    korisnici
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) NULL
)
;

CREATE TABLE
    restorani
(
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(200) NOT NULL,
    adresa VARCHAR(1024) NULL
)
;

CREATE TABLE
    rezervacije
(
    id_korisnik INTEGER NOT NULL,
    id_restorani INTEGER NOT NULL,
    rezervisan DATE NOT NULL,
    od Tname NULL,
    dot Tname NULL
)
;

CREATE VIEW
    v_rezervacije
AS SELECT
    boo.id_korisnik,
    usr.name AS korisnik_ime,
    boo.id_restorani,
    roo.name AS restoran_ime,
    boo.rezervisan,
    boo.od,
    boo.dot
FROM
    rezervacije AS boo
JOIN korisnici AS usr ON
    usr.id = boo.id_korisnik
JOIN restorani AS roo ON
    roo.id = boo.id_restorani
;
