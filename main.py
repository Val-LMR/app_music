from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from functools import wraps

app = Flask(__name__)
app.secret_key = "admin"

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="user",
        password="rootroot",
        database="record_company"
    )


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


@app.route("/")
@login_required
def index():
    return render_template("index.html")


def search(mot):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
    SELECT name, 'album' AS type FROM albums WHERE name LIKE %s
    UNION
    SELECT name, 'groupe' AS type FROM bands WHERE name LIKE %s
    UNION
    SELECT name, 'chanson' AS type FROM songs WHERE name LIKE %s
""", (f"%{mot}%", f"%{mot}%", f"%{mot}%"))
    resultats = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultats

@app.route("/recherche")
@login_required
def recherche():
    q = request.args.get("q", "")
    resultats = search(q) if q else []
    return render_template("index.html", q=q, resultats=resultats)


def get_namebdd():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT name FROM bands""")
    resultats = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultats

def get_albumsyear():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT albums.name AS album_name,
               albums.release_year,
               bands.name AS band_name
        FROM bands
        INNER JOIN albums ON bands.id = albums.band_id
    """)
    resultats = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultats

def get_albumsprgroupe(nom_groupe):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT albums.name AS album_name, albums.release_year
        FROM bands
        INNER JOIN albums ON bands.id = albums.band_id
        WHERE bands.name = %s
    """, (nom_groupe,))
    resultats = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultats

def get_albumsprannee(annee_album):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT name FROM albums WHERE release_year = %s""", (annee_album,))
    resultats = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultats

def check_login(login, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id FROM users WHERE login = %s AND password = MD5(%s)
    """, (login, password))
    resultat = cursor.fetchone()
    cursor.close()
    conn.close()

    return resultat is not None

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifiant = request.form["login"]
        mdp = request.form["password"]
        if check_login(identifiant, mdp):
            session["user"] = identifiant
            return redirect(url_for("index"))
        flash("Login ou mot de passe incorrect")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def modify_password(newpwd, login):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""UPDATE users SET password = MD5(%s) WHERE login = %s""", (newpwd, login))
    conn.commit()
    resultats = cursor.rowcount
    cursor.close()
    conn.close()
    return resultats


"""print("Bonjour, que voulez vous faire ?\n")
print("Choix 1 : Afficher les noms des groupes présents dans la bdd\n")
print("Choix 2 : Afficher la liste des albums avec leur année de publication et le groupe qui les a enregistrés\n")
print("Choix 3 : Afficher les albums d'un groupe\n")
print("Choix 4 : Afficher les albums sortis pour une année précise\n")
print("Choix 5 : Modifier votre mot de passe\n")
print("Choix 6 : Faire une recherche sur les albums et les groupes\n")
print("Choix 9 : Quitter\n")

choix = input("Faites votre choix : ")
print("\n")

if choix == "1":
    noms = get_namebdd()
    for n in noms:
        print(n["name"])
elif choix == "2":
    albums = get_albumsyear()
    for a in albums:
        print(f"{a['album_name']} - {a['release_year']} - {a['band_name']}")
elif choix == "3":
    nom = input("Donner le nom du groupe exact à rechercher : ")
    search_groupe = get_albumsprgroupe(nom)
    for a in search_groupe:
        print(f"{a['album_name']} - {a['release_year']}")
elif choix == "4":
    annee = int(input("Donnez l'année de recherche : "))
    search_year = get_albumsprannee(annee)
    for a in search_year:
        print(a["name"])

elif choix == "5":
    identifiant = input("Quel est votre login ? ")
    newpwd = input("Quel est votre nouveau mot de passe ? ")
    mdp = modify_password(newpwd, identifiant)


elif choix == "6":
    mot = input("Quel est votre recherche ? ")
    resultats_recherche = search(mot)

elif choix == "9":
    exit()
else:
    print("Veuillez choisir un numéro valable")
"""
app.run(debug=True)
