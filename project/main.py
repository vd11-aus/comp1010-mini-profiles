from flask import *
import os.path
import firebase_admin
from firebase_admin import *
from firebase_admin import firestore

cred = credentials.Certificate("other-files\miniprofiles-801b3-firebase-adminsdk-a02t1-8cb3692aa2.json")
firebase_admin.initialize_app(cred)

db_link = firestore.client()

app = Flask(__name__)

app.config['SECRET_KEY'] = "25ca747914f8d844c9256dfba73c39fe1ae62290da552a7f14d83e194aa98edd"

def write_json(data, filename):
    f = open(f'JSON/{filename}.json', 'w')
    f.write(json.dumps(data))
    f.close()

def read_json(filename):
    f = open(f'JSON/{filename}.json', 'r')
    data = json.loads(f.read())
    f.close()
    return data

@app.route("/", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        if "zid" in request.form:
            credentials_grab = db_link.collection("credentials").document(request.form["zid"]).get()
            if credentials_grab.exists:
                credentials_dict = credentials_grab.to_dict()
                if credentials_dict["password"] != request.form["password"]:
                    return redirect(url_for("error", reasoncode = "101"))
                return redirect(url_for("home"))
            else:
                return redirect(url_for("error", reasoncode = "404"))
        if "createaccount" in request.form:
            return redirect(url_for("tester"))
    return render_template("signin.html")

@app.route("/create-account", methods=["GET", "POST"])
def createaccount():
    return "Hello World"

@app.route("/home", methods=["GET", "POST"])
def home():
    return "Welcome back!"

@app.route("/error/<reasoncode>", methods=["GET", "POST"])
def error(reasoncode):
    return reasoncode

if __name__ == "__main__":
    app.run(debug=True)