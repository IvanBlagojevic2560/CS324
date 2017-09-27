#!/usr/bin/python
import os, sys
import cgi
import datetime
import sqlite3
from wsgiref.util import setup_testing_defaults, shift_path_info
from wsgiref.simple_server import make_server

DATABASE_FILEPATH = "rezervacije.db"

def napraviBazu():
    """ Povezivanje sa bazom 
    """
 
    if os.path.exists(DATABASE_FILEPATH):
        os.remove(DATABASE_FILEPATH)

  
    db = sqlite3.connect(DATABASE_FILEPATH)
    q = db.cursor()

    
    sql = open("baza.sql").read()

   
    statements = sql.split(";")

    
    for statement in statements:
        q.execute(statement)

    q.close()
    db.commit()
    db.close()

def popuniBazu():
    """Popunjavanje baze podataka
    """
    db = sqlite3.connect(DATABASE_FILEPATH)
    q = db.cursor()

    sql = "INSERT INTO korisnici(id, name, email) VALUES(?, ?, ?)"
    q.execute(sql, [1, "Marko Nikolic", "mn@gmail.com"])
    q.execute(sql, [2, "Darko Savic", "donald.duck@gmail.com"])
    q.execute(sql, [3, "Ilica Cabic", None])

    sql = "INSERT INTO restorani(id, name, adresa) VALUES(?, ?, ?)"
    q.execute(sql, [1, "Restoran Albatros", "Kneza Milosa 4"])
    q.execute(sql, [2, "Restoran Mijic", "Diljska 6"])
    q.execute(sql, [3, "Restoran Babic", "Bastenska 7"])

  
    sql = """
    INSERT INTO
        rezervacije
    (
        id_restorani, id_korisnik, rezervisan, od, dot
    )
    VALUES(
        ?, ?, ?, ?, ?
    )"""
    q.execute(sql, [1, 1, '2014-09-25', '09:00', '10:00'])
    q.execute(sql, [3, 1, '2015-09-25', None, None])
    q.execute(sql, [2, 3, '2014-09-22', '12:00', None]) 
    q.execute(sql, [1, 2, '2015-02-14', '09:30', '10:00'])

    q.close()
    db.commit()
    db.close()

def select(sql_statement, params=None):
    """Citanje iz baze podataka
    """
    if params is None:
        params = []
    db = sqlite3.connect(DATABASE_FILEPATH)
    db.row_factory = sqlite3.Row
    q = db.cursor()
    try:
        q.execute(sql_statement, params)
        return q.fetchall()
    finally:
        q.close()
        db.close()

def execute(sql_statement, params=None):
    """Unos podataka u bazi
    """
    if params is None:
        params = []
    db = sqlite3.connect(DATABASE_FILEPATH)
    q = db.cursor()
    try:
        q.execute(sql_statement, params)
        db.commit()
    finally:
        q.close()
        db.close()

def get_korisnik(id_korisnik):
    """Vracanje korisnika sa odredjenim id-om
    """
    for korisnik in select("SELECT * FROM korisnici WHERE id = ?", [id_korisnik]):
        return korisnik

def get_restoran(id_restorani):
    """Vracanje resotrana sa odredjenim id-om
    """
    for restoran in select("SELECT * FROM restorani WHERE id = ?", [id_restorani]):
        return restoran

def get_sveKorisnike():
    """Vracanje svih korisnika koji se nalaze u bazi
    """
    return select("SELECT * FROM korisnici")

def get_sveRestorane():
    """Vracanje svih restorana koji se nalaze u bazi
    """
    return select("SELECT * FROM restorani")

def get_rezervacije():
    """Vracanje svih rezervacija koji su u bazi
    """
    return select("SELECT * FROM v_rezervacije")

def get_rezervacijeZaOdredjenogKorisnika(id_korisnik):
    """Vracanje svih rezervacija za odredjenog korisnika
    """
    return select("SELECT * FROM v_rezervacije WHERE id_korisnik = ?", [id_korisnik])

def rezervacije_restorana_page(id_restorani):
    """Vracanje svih rezervacija za odredjeni restoran
    """
    return select("SELECT * FROM v_rezervacije WHERE id_restorani = ?", [id_restorani])

def dodajOsobu(name, email):
    """Dodavanje korisnika u bazu
    """
    print("%r, %r" % (name, email))
    execute(
        "INSERT INTO korisnici(name, email) VALUES (?, ?)",
        [name, email]
    )

def dodajRestoran(name, adresa):
    """Dodavanje restorana u bazu podataka 
    """
    execute(
        "INSERT INTO restorani(name, adresa) VALUES (?, ?)",
        [name, adresa]
    )

def napraviRezervaciju(id_korisnik, id_restorani, rezervisan, od=None, dot=None):
    """Dodavanje rezervacije u bazu
    """
    execute(
        """
        INSERT INTO rezervacije(id_korisnik, id_restorani, rezervisan, od, dot)
        VALUES(?, ?, ?, ?, ?)
        """,
        [id_korisnik, id_restorani, rezervisan, od, dot]
    )

def page(title, content):
    """ Vracanje cele HTML strane
    """
    return """
    <html>
    <head>
    <title>Sistem za rezervaciju restorana {title}</title>
    <style>
    body {{
        background-colour : #cff;
        margin : 1em;
        padding : 1em;
        border : thin solid black;
        font-family : sans-serif;
    }}
    td {{
        padding : 0.5em;
        margin : 0.5em;
        border : thin solid blue;
    }}

    </style>
    </head>
    <body>
    <h1>{title}</h1>
    {content}
    </body>
    </html>
    """.format(title=title, content=content)

def pocetnaStrana(environ):
    """Pocetna strana koja sadrzi sve moguce strane sistema 
    """
    html = """
    <ul>
        <li><a href="/korisnici">Korisnici</a></li>
        <li><a href="/restorani">Restorani</a></li>
        <li><a href="/rezervacije">Rezervacije</a></li>
    </ul>
    """
    return page("Rezervacije", html)

def korisnici_page(environ):
    """Stranica sa listom korisnika povezana sa svim rezervacijama tog korisnika
    """
    html = "<ul>"
    for korisnik in get_sveKorisnike():
        html += '<li><a href="/rezervacije/korisnik/{id}">{name}</a> ({email})</li>\n'.format(
            id=korisnik['id'],
            name=korisnik['name'],
            email=korisnik['email'] or "No email"
        )
    html += "</ul>"
    html += "<hr/>"
    html += """<form method="POST" action="/add-korisnik">
    <label for="name">Ime:</label>&nbsp;<input type="text" name="name"/>
    <label for="email">Email:</label>&nbsp;<input type="text" name="email"/>
    <input type="submit" name="submit" value="Dodaj korisnika"/>
    </form>"""
    return page("Korisnici", html)

def restoran_page(environ):
    """Stranica sa listom restorana, povezana sa njenim rezervacijama
    """
    html = "<ul>"
    for restoran in get_sveRestorane():
        html += '<li><a href="/rezervacije/restoran/{id}">{name}</a> ({adresa})</li>\n'.format(
            id=restoran['id'],
            name=restoran['name'],
            adresa=restoran['adresa'] or "Location unknown"
        )
    html += "</ul>"
    html += "<hr/>"
    html += """<form method="POST" action="/add-restoran">
    <label for="name">Ime:</label>&nbsp;<input type="text" name="name"/>
    <label for="adresa">Lokacija:</label>&nbsp;<input type="text" name="adresa"/>
    <input type="submit" name="submit" value="Dodaj restoran"/>
    </form>"""
    return page("Restoran", html)

def all_rezervacije_page(environ):
    """Stranica sa svim rezervacijama
    """
    html = "<table>"
    html += "<tr><td>Ime korisnikan</td><td>Restoran</td><td>Datum</td><td>Vreme</td></tr>"
    for rezervacija in get_rezervacije():
        html += "<tr><td>{korisnik_ime}</td><td>{restoran_ime}</td><td>{rezervisan}</td><td>{od} - {dot}</td></tr>".format(
     
           restoran_ime=rezervacija['restoran_ime'],
           korisnik_ime=rezervacija['korisnik_ime'],
            rezervisan=rezervacija['rezervisan'],
            od=rezervacija['od'] or "",
            dot=rezervacija['dot'] or ""
        )
    html += "</table>"

    html += "<hr/>"
    html += '<form method="POST" action="/add-rezervacija">'

    html += '<label for="id_korisnik">Korisnik:</label>&nbsp;<select name="id_korisnik">'
    for korisnik in get_sveKorisnike():
        html += '<option value="{id}">{name}</option>'.format(**korisnik)
    html += '</select>'

    html += '&nbsp;|&nbsp;'

    html += '<label for="id_restorani">Restoran:</label>&nbsp;<select name="id_restorani">'
    for restoran in get_sveRestorane():
        html += '<option value="{id}">{name}</option>'.format(**restoran)
    html += '</select>'

    html += '&nbsp;|&nbsp;'
    html += '<label for="rezervisan">Datum</label>&nbsp;<input type="text" name="rezervisan" value="{today}"/>'.format(today=datetime.date.today())
    html += '&nbsp;<label for="od">Izmedju</label>&nbsp;<input type="text" name="od" />'
    html += '&nbsp;<label for="dot">i</label>&nbsp;<input type="text" name="dot" />'
    html += '<input type="submit" name="submit" value="Dodaj rezervaciju"/></form>'

    return page("Sve rezervacije", html)


def rezervacije_korisnik_page(environ):
    
    id_korisnik = int(shift_path_info(environ))
    korisnik = get_korisnik(id_korisnik)
    html = "<table>"
    html += "<tr><td>Restoran</td><td>Datum</td><td>Vreme</td></tr>"
    for rezervacija in get_rezervacijeZaOdredjenogKorisnika(id_korisnik):
        html += "<tr><td>{korisnik_ime}</td><td>{rezervisan}</td><td>{od} - {dot}</td></tr>".format(
            korisnik_ime=rezervacija['korisnik_ime'],
            rezervisan=rezervacija['rezervisan'],
            od=rezervacija['od'] or "",
            dot=rezervacija['dot'] or ""
        )
    html += "</table>"
    html += "<hr/>"
    html += '<form method="POST" action="/add-rezervacija">'
    html += '<input type="hidden" name="id_korisnik" value="{id_korisnik}"/>'.format(id_korisnik=id_korisnik)
    html += '<label for="id_restorani">Restorani:</label>&nbsp;<select name="id_restorani">'
    for restoran in get_sveRestorane():
        html += '<option value="{id}">{name}</option>'.format(**restoran)
    html += '</select>'
    html += '&nbsp;|&nbsp;'
    html += '<label for="rezervisan">Datum</label>&nbsp;<input type="text" name="rezervisan" value="{today}"/>'.format(today=datetime.date.today())
    html += '&nbsp;<label for="od">izmedju</label>&nbsp;<input type="text" name="od" />'
    html += '&nbsp;<label for="dot">i</label>&nbsp;<input type="text" name="dot" />'
    html += '<input type="submit" name="submit" value="Dodaj rezervaciju"/></form>'
    return page("Rezervacija za %s" % korisnik['name'], html)

def rezervacije_restorani_page(environ):
    
    id_restorani = int(shift_path_info(environ))
    restoran = get_restoran(id_restorani)
    html = "<table>"
    html += "<tr><td>Korisnik</td><td>Datum</td><td>Vreme</td></tr>"
    for rezervacija in rezervacije_restorani_page(id_restorani):
        html += "<tr><td>{restoran_ime}</td><td>{rezervisan}</td><td>{od} - {dot}</td></tr>".format(
            restoran_ime=rezervacija['restoran_ime'],
            rezervisan=rezervacija['rezervisan'],
            od=rezervacija['od'] or "",
            dot=rezervacija['dot'] or ""
        )
    html += "</table>"
    html += "<hr/>"
    html += '<form method="POST" action="/add-rezervacija">'
    html += '<input type="hidden" name="id_restorani" value="{id_restorani}"/>'.format(id_restorani=id_restorani)
    html += '<label for="id_korisnik">Korisnik:</label>&nbsp;<select name="id_korisnik">'
    for korisnik in get_sveKorisnike():
        html += '<option value="{id}">{name}</option>'.format(**korisnik)
    html += '</select>'
    html += '&nbsp;|&nbsp;'
    html += '<label for="rezervisan">Rezervisan</label>&nbsp;<input type="text" name="rezervisan" value="{today}"/>'.format(today=datetime.date.today())
    html += '&nbsp;<label for="od">izmedju</label>&nbsp;<input type="text" name="od" />'
    html += '&nbsp;<label for="dot">i</label>&nbsp;<input type="text" name="dot" />'
    html += '<input type="submit" name="submit" value="Dodaj rezervaciju"/></form>'
    return page("Rezervacija za  %s" % restoran['name'], html)

def rezervacije_page(environ):
   
    category = shift_path_info(environ)
    if not category:
        return all_rezervacije_page(environ)
    elif category == "korisnik":
        return rezervacije_korisnik_page(environ)
    elif category == "restoran":
        return rezervacije_restorani_page(environ)
    else:
        return "page not found"

def add_korisnik(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ.copy(), keep_blank_values=True)
    dodajOsobu(form.getfirst("name"), form.getfirst('email', ""))

def add_soba(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ.copy(), keep_blank_values=True)
    dodajRestoran(form.getfirst("name"), form.getfirst('adresa', None))

def add_rezervacija(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ.copy(), keep_blank_values=True)
    napraviRezervaciju(
        form.getfirst("id_korisnik"),
        form.getfirst("id_restorani"),
        form.getfirst("rezervisan"),
        form.getfirst("od"),
        form.getfirst("dot")
    )

def webapp(environ, start_response):

    setup_testing_defaults(environ)

    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
  
    param1 = shift_path_info(environ)
    if param1 == "":
        data = pocetnaStrana(environ)
    elif param1 == "korisnici":
        data = korisnici_page(environ)
    elif param1 == "restorani":
        data = restoran_page(environ)
    elif param1 == "rezervacije":
        data = rezervacije_page(environ)
    elif param1 == "add-korisnik":
        add_korisnik(environ)
        status = "301 Redirect"
        headers.append(("Location", "/korisnici"))
        data = ""
    elif param1 == "add-restoran":
        add_soba(environ)
        status = "301 Redirect"
        headers.append(("Location", "/restorani"))
        data = ""
    elif param1 == "add-rezervacija":
        add_rezervacija(environ)
        status = "301 Redirect"
        headers.append(("Location", environ.get("HTTP_REFERER", "/rezervacije")))
        data = ""
    else:
        status = '404 Not Found'
        data = "Not Found: %s" % param1

    start_response(status, headers)
    return [data.encode("utf-8")]

def run_website():
    httpd = make_server('', 8000, webapp)
    print("Serving on port 8000...")
    httpd.serve_forever()

if __name__ == '__main__':
    print("Pravljenje baze %s" % DATABASE_FILEPATH)
    napraviBazu()
    print("Unosenje definisanih podataka u bazu %s" % DATABASE_FILEPATH)
    popuniBazu()
    print("Pokretanje webservera")
    run_website()
    print("Finished")
