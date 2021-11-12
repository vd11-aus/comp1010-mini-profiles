from os import write
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
    f = open(f'project/JSON/{filename}.json', 'w')
    f.write(json.dumps(data))
    f.close()

def read_json(filename):
    f = open(f'project/JSON/{filename}.json', 'r')
    data = json.loads(f.read())
    f.close()
    return data

def create_user(zid, password):
    credentials_data = {
        "zId": zid,
        "password": password
    }
    profile_data = {
        "name": "",
        "gender": "",
        "aboutMe": "",
    }
    fs_link.collection("credentials").document(zid).set(credentials_data)
    fs_link.collection("profiles").document(zid).set(profile_data)

@app.route("/", methods=["GET", "POST"])
def signin():
    session["currentuser"] = ""
    if request.method == "POST":
        if "signin" in request.form:
            credentials_grab = fs_link.collection("credentials").document(request.form["zid"]).get()
            if credentials_grab.exists:
                credentials_dict = credentials_grab.to_dict()
                if credentials_dict["password"] != request.form["password"]:
                    return redirect(url_for("error", reasoncode = "100", previouspage = "signin"))
                session["currentuser"] = request.form["zid"]
                return redirect(url_for("home"))
            else:
                return redirect(url_for("error", reasoncode = "101", previouspage = "signin"))
        if "createaccount" in request.form:
            return redirect(url_for("createaccount"))
    return render_template("signin.html")

@app.route("/create-account", methods=["GET", "POST"])
def createaccount():
    session["currentuser"] = ""
    if request.method == "POST":
        if "cancelcreateaccount" in request.form:
            return redirect(url_for("signin"))
        if "confirmcreateaccount" in request.form:
            current_user_grab = fs_link.collection("credentials").document(request.form["zid"]).get()
            if current_user_grab.exists:
                return redirect(url_for("error", reasoncode = "200", previouspage = "createaccount"))
            number_count = 0
            for character in request.form["zid"]:
                if character in string.digits:
                    number_count += 1
            if len(request.form["zid"]) != 8 or request.form["zid"][0] != "z" or number_count != 7:
                return redirect(url_for("error", reasoncode = "201", previouspage = "createaccount"))
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
                elif character in string.ascii_uppercase:
                    number_upper_case += 1
            if number_lower_case == 0 or number_upper_case == 0 or number_digits == 0:
                password_valid = False
            if password_valid == False:
                return redirect(url_for("error", reasoncode = "202", previouspage = "createaccount"))
            if request.form["password"] != request.form["confirmpassword"]:
                return redirect(url_for("error", reasoncode = "203", previouspage = "createaccount"))
            create_user(request.form["zid"], request.form["password"])
            return redirect(url_for("signin"))
    return render_template("createaccount.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    if session["currentuser"] == "":
        return redirect(url_for("error", reasoncode = "900", previouspage = "signin"))
    profile_data_grab = fs_link.collection("profiles").document(session["currentuser"]).get()
    if profile_data_grab.exists:
        profile_data = profile_data_grab.to_dict()
    profile_name = profile_data["name"]
    newsfeed_data_grab = fs_link.collection("other").document("newsfeed").get()
    if newsfeed_data_grab.exists:
        newsfeed_data = newsfeed_data_grab.to_dict()["articlelist"]
        flipped_data = newsfeed_data[::-1]
        newest_to_oldest = flipped_data[0:11]
    if request.method == "POST":
        if "logout" in request.form:
            session["currentuser"] = ""
            return redirect(url_for("signin"))
        if "settings" in request.form:
            return redirect(url_for("settings"))
        if "home" in request.form:
            return redirect(url_for("home"))
        if "viewstudent" in request.form:
            return redirect(url_for("viewstudent"))
        if "searchbyclass" in request.form:
            return redirect(url_for("searchbyclass"))
    return render_template("home.html", name = profile_name, zid = session["currentuser"], newsfeed = newest_to_oldest)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if session["currentuser"] == "":
        return redirect(url_for("error", reasoncode = "900", previouspage = "signin"))
    profile_data_grab = fs_link.collection("profiles").document(session["currentuser"]).get()
    if profile_data_grab.exists:
        profile_data = profile_data_grab.to_dict()
    profile_name = profile_data["name"]
    if request.method == "POST":
        if "logout" in request.form:
            session["currentuser"] = ""
            return redirect(url_for("signin"))
        if "settings" in request.form:
            return redirect(url_for("settings"))
        if "home" in request.form:
            return redirect(url_for("home"))
        if "viewstudent" in request.form:
            return redirect(url_for("viewstudent"))
        if "searchbyclass" in request.form:
            return redirect(url_for("searchbyclass"))
    return render_template("settings.html", name = profile_name, zid = session["currentuser"])

@app.route("/error/<reasoncode>-from-<previouspage>", methods=["GET", "POST"])
def error(reasoncode, previouspage):
    if request.method == "POST":
        if "redirectme" in request.form:
            return redirect(url_for(previouspage))
    error_directory_grab = fs_link.collection("other").document("errordirectory").get()
    if error_directory_grab.exists:
        dataset = error_directory_grab.to_dict()
        dynamic_data = dataset["errordirectory"]
    write_json(dynamic_data, "error-list")
    error_directory = read_json("error-list")
    title = error_directory[reasoncode]["title"]
    reason = error_directory[reasoncode]["reason"]
    return render_template("error.html", errortitle = title, errornumber = reasoncode, errormessage = reason, redirectpath = previouspage)

@app.route("/<randomurl>", methods=["GET", "POST"])
def nothingfound(randomurl):
    if request.method == "POST":
        return redirect(url_for("signin"))
    return render_template("randomurl.html", url = randomurl)

if __name__ == "__main__":
    app.run(debug=True)