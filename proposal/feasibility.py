#imports
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import *
from pyhtml import html, h1, p, form, input_, br

#establish database connection - please contact me to view database structure
cred = credentials.Certificate("other-files\miniprofiles-801b3-firebase-adminsdk-a02t1-8cb3692aa2.json")
firebase_admin.initialize_app(cred)

db_link = firestore.client()

#create app
app = Flask(__name__)

#main page - navigation
@app.route('/', methods=["GET", "POST"])
def main():
    sample_credentials = {
        "z1234567": {
            "password": "password123",
            "dob": "01/01/2021"
        },
        "z7654321": {
            "password": "321password",
            "dob": "31/12/2021"
        },
    }
    if request.method == "POST":
        if "manageaccount" in request.form:
            return redirect(url_for("manage_account"))
        if "viewstudent" in request.form:
            return redirect(url_for("view_student"))
    design = html(
        form(
            input_(type="submit", name="manageaccount", value="Manage Account"),
        ),
        h1("Main Menu"),
        p("Sample Credentials: " + str(sample_credentials)),
        form(
            input_(type="submit", name="viewstudent", value="View Student"),
            br
        )
    )
    return str(design)

#enter student id to view profile
@app.route('/viewstudent', methods=["GET", "POST"])
def view_student():
    if request.method == "POST":
        zid_list = []
        zid_grab = db_link.collection("profiles").get()
        for profile in zid_grab:
            zid_list.append(profile.to_dict()["zid"])
        if "viewid" in request.form:
            input = request.form["zidinput"]
            if len(input) != 8 or input[0] != "z":
                return redirect(url_for("error", reasoncode = "001"))
            elif zid_list.count(input) == 0:
                return redirect(url_for("error", reasoncode = "003"))
            else:
                return redirect(url_for("zid_profile", zid = request.form["zidinput"]))
    design = html(
        h1("View Student"),
        form(
            input_(type="text", name="zidinput"),
            input_(type="submit", name="viewid", value="View")
        )
    )
    return str(design)

#view profile results
@app.route('/viewstudent/<zid>', methods=["GET", "POST"])
def zid_profile(zid):
    profile_grab = db_link.collection('profiles').document(zid).get()
    if profile_grab.exists:
        profile_data_dict = profile_grab.to_dict()
    design = html(
        h1(zid + "'s Profile"),
        p("Name: " + profile_data_dict["name"]),
        p("Gender: " + profile_data_dict["gender"]),
        p("About Me: " + profile_data_dict["aboutMe"])
    )
    return str(design)

#sign in to account
@app.route('/manageaccount', methods=["GET", "POST"])
def manage_account():
    if request.method == "POST":
        if "signin" in request.form:
            input_credentials = ["", "", ""]
            actual_credentials = ["", "", ""]
            all_correct = True
            input_credentials[0] = request.form["username"]
            input_credentials[1] = request.form["password"]
            input_credentials[2] = request.form["dob"]
            credentials_grab = db_link.collection('credentials').document(input_credentials[0]).get()
            if credentials_grab.exists:
                credentials_dict = credentials_grab.to_dict()
                actual_credentials[0] = credentials_dict["zid"]
                actual_credentials[1] = credentials_dict["password"]
                actual_credentials[2] = credentials_dict["dob"]
                for item in range(3):
                    if actual_credentials[item] != input_credentials[item]:
                        all_correct = False
            else:
                all_correct = False
            if all_correct:
                return redirect(url_for("edit_profile", zid = input_credentials[0]))
            else:
                return redirect(url_for("error", reasoncode = "002"))
    design = html(
        h1("Manage Account"),
        form(
            p("zID: "),
            input_(type = "text", name = "username", required = "required"),
            p("Password: "),
            input_(type = "password", name = "password", required = "required"),
            p("Date of Birth: "),
            input_(type = "text", name = "dob", required = "required"),
            br,
            br,
            input_(type = "submit", name = "signin", value ="Sign In"),
        )
    )
    return str(design)

#edit account
@app.route('/editprofile/<zid>', methods=["GET", "POST"])
def edit_profile(zid):
    profile_grab = db_link.collection('profiles').document(zid).get()
    if profile_grab.exists:
        profile_data_dict = profile_grab.to_dict()
    if request.method == "POST":
        if "savechanges" in request.form:
            db_link.collection('profiles').document(zid).update({"name":request.form["name"]})
            db_link.collection('profiles').document(zid).update({"gender":request.form["gender"]})
            db_link.collection('profiles').document(zid).update({"aboutMe":request.form["aboutme"]})
        return redirect(url_for("main"))
    design = html(
        h1(zid + " - Edit Profile"),
        form(
            p("Name: "),
            input_(type = "text", name = "name", required = "required", value = profile_data_dict["name"]),
            p("Gender: "),
            input_(type = "text", name = "gender", required = "required", value = profile_data_dict["gender"]),
            p("About Me: "),
            input_(type = "text", name = "aboutme", required = "required", value = profile_data_dict["aboutMe"]),
            br,
            br,
            input_(type = "submit", name = "cancel", value = "Cancel"),
            input_(type = "submit", name = "savechanges", value = "Save Changes")
        )
    )
    return str(design)

#error feedback
@app.route('/error/<reasoncode>', methods=["GET", "POST"])
def error(reasoncode):
    reasoncodes_dict = {
        "001": "Invalid zID search.",
        "002": "Account credentials incorrect.",
        "003": "Profile doesn't exist for zID."
    }
    design = html(
        h1("Error:" + reasoncode),
        p(reasoncodes_dict[reasoncode])
    )
    return str(design)

if __name__ == "__main__":
    app.run(debug=True)