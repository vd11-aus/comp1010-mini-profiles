from flask import *
import os.path
import firebase_admin
from firebase_admin import *
from firebase_admin import firestore
from firebase_admin import db
import string

cred = credentials.Certificate("other-files\miniprofiles-801b3-firebase-adminsdk-a02t1-8cb3692aa2.json")
firebase_admin.initialize_app(cred)

fs_link = firestore.client()

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

def create_user(zid, password):
    credentials_data = {
        "zid": zid,
        "password": password
    }
    profile_data = {
        "name": "",
        "gender": "",
        "aboutme": "",
    }
    fs_link.collection("credentials").document(zid).set(credentials_data)
    fs_link.collection("profiles").document(zid).set(profile_data)

jsonlist = ["error-list"]

for filename in jsonlist:
    if os.path.exists(f"JSON/{filename}.json") == False:
        write_json({}, filename)

@app.route("/", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        if "signin" in request.form:
            credentials_grab = fs_link.collection("credentials").document(request.form["zid"]).get()
            if credentials_grab.exists:
                credentials_dict = credentials_grab.to_dict()
                if credentials_dict["password"] != request.form["password"]:
                    return redirect(url_for("error", reasoncode = "100"))
                return redirect(url_for("home"))
            else:
                return redirect(url_for("error", reasoncode = "101"))
        if "createaccount" in request.form:
            return redirect(url_for("createaccount"))
    return render_template("signin.html")

@app.route("/create-account", methods=["GET", "POST"])
def createaccount():
    if request.method == "POST":
        if "cancelcreateaccount" in request.form:
            return redirect(url_for("signin"))
        if "confirmcreateaccount" in request.form:
            current_user_grab = fs_link.collection("credentials").document(request.form["zid"]).get()
            if current_user_grab.exists:
                return redirect(url_for("error", reasoncode = "200"))
            number_count = 0
            for character in request.form["zid"]:
                if character in string.digits:
                    number_count += 1
            if len(request.form["zid"]) != 8 or request.form["zid"][0] != "z" or number_count != 7:
                return redirect(url_for("error", reasoncode = "201"))
            password_valid = True
            number_lower_case = 0
            number_upper_case = 0
            number_digits = 0
            if len(request.form["password"]) < 8:
                password_valid = False
            for character in request.form["password"]:
                if character in string.digits:
                    number_digits += 1
                elif character in string.ascii_lowercase:
                    number_lower_case += 1
                elif character in string.string.ascii_uppercase:
                    number_upper_case += 1
            if number_lower_case == 0 or number_upper_case == 0 or number_digits == 0:
                password_valid = False
            if password_valid == False:
                return redirect(url_for("error", reasoncode = "202"))
            if request.form["password"] != request.form["confirmpassword"]:
                return redirect(url_for("error", reasoncode = "203"))
            return redirect(url_for("home"))
    return render_template("createaccount.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    return "Welcome back!"

@app.route("/error/<reasoncode>", methods=["GET", "POST"])
def error(reasoncode):
    return reasoncode

if __name__ == "__main__":
    app.run(debug=True)