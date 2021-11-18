from os import write
from flask import *
import firebase_admin
from firebase_admin import *
from firebase_admin import firestore
from firebase_admin import storage
import string
import urllib.request
import random

cred = credentials.Certificate("other-files\miniprofiles-801b3-firebase-adminsdk-a02t1-8cb3692aa2.json")
firebase_admin.initialize_app(cred, {
    "storageBucket": "miniprofiles-801b3.appspot.com"
})

fs_link = firestore.client()
st_link = storage.bucket()

app = Flask(__name__)

app.config['SECRET_KEY'] = "25ca747914f8d844c9256dfba73c39fe1ae62290da552a7f14d83e194aa98edd"

def background_generator():
    background_data_grab = fs_link.collection("other").document("backgrounds").get()
    if background_data_grab.exists:
        background_data = background_data_grab.to_dict()["backgrounds"]
    random.shuffle(background_data)
    return background_data[0]

def write_json(data, filename):
    f = open(f'project/JSON/{filename}.json', 'w')
    f.write(json.dumps(data))
    f.close()

def read_json(filename):
    f = open(f'project/JSON/{filename}.json', 'r')
    data = json.loads(f.read())
    f.close()
    return data

def check_password_strength(password):
    password_valid = True
    number_lower_case = 0
    number_upper_case = 0
    number_digits = 0
    if len(password) < 8:
        password_valid = False
    for character in password:
        if character in string.digits:
            number_digits += 1
        elif character in string.ascii_lowercase:
            number_lower_case += 1
        elif character in string.ascii_uppercase:
            number_upper_case += 1
    if number_lower_case == 0 or number_upper_case == 0 or number_digits == 0:
        password_valid = False
    return password_valid

def create_user(zid, password):
    credentials_data = {
        "zId": zid,
        "password": password
    }
    st_link.blob(f"icons/{zid}.png").upload_from_filename(r"project/static/assets/default-profile-user.png")
    profile_data = {
        "name": "Change Name",
        "gender": "Undisclosed",
        "aboutMe": "",
        "interests": "",
        "facebook": "",
        "twitter": "",
        "instagram": ""
    }
    fs_link.collection("credentials").document(zid).set(credentials_data)
    fs_link.collection("profiles").document(zid).set(profile_data)
    userset_data_grab = fs_link.collection("profiles").document("userset").get()
    if userset_data_grab.exists:
        userset = userset_data_grab.to_dict()
    userset[zid] = "Change Name"
    fs_link.collection("profiles").document("userset").set(userset)

def update_icon():
    userid = session["currentuser"]
    iconreference = st_link.blob(f"icons/{userid}.png").generate_signed_url(datetime.timedelta(seconds=300), method='GET')
    urllib.request.urlretrieve(iconreference, r"project/static/assets/actual-profile-user.png")

def save_profile(name, gender, aboutme, interests, facebook, twitter, instagram):
    profile_data = {
        "name": name,
        "gender": gender,
        "aboutMe": aboutme,
        "interests": interests,
        "facebook": facebook,
        "twitter": twitter,
        "instagram": instagram
    }
    fs_link.collection("profiles").document(session["currentuser"]).set(profile_data)
    userset_data_grab = fs_link.collection("profiles").document("userset").get()
    if userset_data_grab.exists:
        userset = userset_data_grab.to_dict()
    userset[session["currentuser"]] = name
    fs_link.collection("profiles").document("userset").set(userset)

def save_courses(selectedcourses):
    course_data_grab = fs_link.collection("other").document("courses").get()
    if course_data_grab.exists:
        course_data = course_data_grab.to_dict()
    unselectedcourses = []
    for key in course_data["courses"]:
        unselectedcourses.append(key)
    for course in selectedcourses:
        unselectedcourses.remove(course)
    for course in selectedcourses:
        if course_data["courses"][course]["students"].count(session["currentuser"]) == 0:
            course_data["courses"][course]["students"].append(session["currentuser"])
    for course in unselectedcourses:
        if course_data["courses"][course]["students"].count(session["currentuser"]) > 0:
            course_data["courses"][course]["students"].remove(session["currentuser"])
    fs_link.collection("other").document("courses").set(course_data)

def save_password(password):
    credentials_data_grab = fs_link.collection("credentials").document(session["currentuser"]).get()
    if credentials_data_grab.exists:
        credentials_data = credentials_data_grab.to_dict()
    credentials_data["password"] = password
    fs_link.collection("credentials").document(session["currentuser"]).set(credentials_data)

def save_strengths(selectedstrengths):
    strength_data_grab = fs_link.collection("other").document("strengths").get()
    if strength_data_grab.exists:
        strength_data = strength_data_grab.to_dict()
    unselectedstrengths = []
    for key in strength_data["strengths"]:
        unselectedstrengths.append(key)
    for strength in selectedstrengths:
        unselectedstrengths.remove(strength)
    for strength in selectedstrengths:
        if strength_data["strengths"][strength]["students"].count(session["currentuser"]) == 0:
            strength_data["strengths"][strength]["students"].append(session["currentuser"])
    for strength in unselectedstrengths:
        if strength_data["strengths"][strength]["students"].count(session["currentuser"]) > 0:
            strength_data["strengths"][strength]["students"].remove(session["currentuser"])
    fs_link.collection("other").document("strengths").set(strength_data)

def filter_students_courses(filters):
    course_data_grab = fs_link.collection("other").document("courses").get()
    if course_data_grab.exists:
        course_data = course_data_grab.to_dict()
    filtered_students = []
    for item in course_data["courses"][filters[0]]["students"]:
        filtered_students.append(str(item))
    students_to_remove = []
    for student in filtered_students:
        for course in filters:
            if course_data["courses"][course]["students"].count(student) == 0:
                students_to_remove.append(str(student))
                break
    for removed in students_to_remove:
        filtered_students.remove(removed)
    userset_data_grab = fs_link.collection("profiles").document("userset").get()
    if userset_data_grab.exists:
        userset = userset_data_grab.to_dict()
    outcome = {}
    for student in filtered_students:
        zidvalue = str(student)
        namevalue = userset[zidvalue]
        iconvalue = st_link.blob(f"icons/{zidvalue}.png").generate_signed_url(datetime.timedelta(seconds=300), method='GET')
        outcome[student] = {}
        outcome[student]["name"] = namevalue
        outcome[student]["icon"] = iconvalue
    session["filterstudentlist"] = outcome

def filter_students_strengths(filters):
    strength_data_grab = fs_link.collection("other").document("strengths").get()
    if strength_data_grab.exists:
        strength_data = strength_data_grab.to_dict()
    filtered_students = []
    for item in strength_data["strengths"][filters[0]]["students"]:
        filtered_students.append(str(item))
    students_to_remove = []
    for student in filtered_students:
        for strength in filters:
            if strength_data["strengths"][strength]["students"].count(student) == 0:
                students_to_remove.append(str(student))
                break
    for removed in students_to_remove:
        filtered_students.remove(removed)
    userset_data_grab = fs_link.collection("profiles").document("userset").get()
    if userset_data_grab.exists:
        userset = userset_data_grab.to_dict()
    outcome = {}
    for student in filtered_students:
        zidvalue = str(student)
        namevalue = userset[zidvalue]
        iconvalue = st_link.blob(f"icons/{zidvalue}.png").generate_signed_url(datetime.timedelta(seconds=300), method='GET')
        outcome[student] = {}
        outcome[student]["name"] = namevalue
        outcome[student]["icon"] = iconvalue
    session["filterstudentlist"] = outcome

# COMPLETE - SIGN IN
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

# COMPLETE - CREATE ACCOUNT
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
            if check_password_strength(request.form["password"]) == False:
                return redirect(url_for("error", reasoncode = "202", previouspage = "createaccount"))
            if request.form["password"] != request.form["confirmpassword"]:
                return redirect(url_for("error", reasoncode = "203", previouspage = "createaccount"))
            create_user(request.form["zid"], request.form["password"])
            session["currentuser"] = request.form["zid"]
            return redirect(url_for("introduction"))
    return render_template("createaccount.html")

# COMPLETE - INTRODUCTION
@app.route("/introduction", methods=["GET", "POST"])
def introduction():
    if session["currentuser"] == "":
        return redirect(url_for("error", reasoncode = "900", previouspage = "signin"))
    update_icon()
    profile_data_grab = fs_link.collection("profiles").document(session["currentuser"]).get()
    if profile_data_grab.exists:
        profile_data = profile_data_grab.to_dict()
    if request.method == "POST":
        if "logout" in request.form:
            session["currentuser"] = ""
            return redirect(url_for("signin"))
        if "settings" in request.form:
            return redirect(url_for("settings"))
        if "home" in request.form:
            return redirect(url_for("home"))
        if "search" in request.form:
            return redirect(url_for("search"))
        if "help" in request.form:
            return redirect(url_for("help"))
    return render_template("introduction.html", name = profile_data["name"], zid = session["currentuser"], backgroundimage = background_generator())

# COMPLETE - HELP
@app.route("/help", methods=["GET", "POST"])
def help():
    if session["currentuser"] == "":
        return redirect(url_for("error", reasoncode = "900", previouspage = "signin"))
    update_icon()
    profile_data_grab = fs_link.collection("profiles").document(session["currentuser"]).get()
    if profile_data_grab.exists:
        profile_data = profile_data_grab.to_dict()
    strength_data_grab = fs_link.collection("other").document("strengths").get()
    if strength_data_grab.exists:
        strength_data = strength_data_grab.to_dict()["strengths"]
    course_data_grab = fs_link.collection("other").document("courses").get()
    if course_data_grab.exists:
        course_data = course_data_grab.to_dict()["courses"]
    if request.method == "POST":
        if "logout" in request.form:
            session["currentuser"] = ""
            return redirect(url_for("signin"))
        if "settings" in request.form:
            return redirect(url_for("settings"))
        if "home" in request.form:
            return redirect(url_for("home"))
        if "search" in request.form:
            return redirect(url_for("search"))
        if "help" in request.form:
            return redirect(url_for("help"))
    return render_template("help.html", name = profile_data["name"], zid = session["currentuser"], strengthlist = strength_data, courselist = course_data,
        backgroundimage = background_generator())

# COMPLETE - HOME
@app.route("/home", methods=["GET", "POST"])
def home():
    if session["currentuser"] == "":
        return redirect(url_for("error", reasoncode = "900", previouspage = "signin"))
    update_icon()
    profile_data_grab = fs_link.collection("profiles").document(session["currentuser"]).get()
    if profile_data_grab.exists:
        profile_data = profile_data_grab.to_dict()
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
        if "search" in request.form:
            return redirect(url_for("search"))
        if "help" in request.form:
            return redirect(url_for("help"))
    return render_template("home.html", name = profile_data["name"], zid = session["currentuser"], newsfeed = newest_to_oldest, 
        backgroundimage = background_generator())

# COMPLETE - SETTINGS
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if session["currentuser"] == "":
        return redirect(url_for("error", reasoncode = "900", previouspage = "signin"))
    update_icon()
    userid = session["currentuser"]
    profile_data_grab = fs_link.collection("profiles").document(userid).get()
    if profile_data_grab.exists:
        profile_data = profile_data_grab.to_dict()
    course_data_grab = fs_link.collection("other").document("courses").get()
    if course_data_grab.exists:
        course_data = course_data_grab.to_dict()["courses"]
    strength_data_grab = fs_link.collection("other").document("strengths").get()
    if strength_data_grab.exists:
        strength_data = strength_data_grab.to_dict()["strengths"]
    acknowledgedstrengths = []
    for strength in strength_data:
        if strength_data_grab.to_dict()["strengths"][strength]["students"].count(userid) > 0:
            acknowledgedstrengths.append(str(strength))
    enrolledcourses = []
    for course in course_data:
        if course_data_grab.to_dict()["courses"][course]["students"].count(userid) > 0:
            enrolledcourses.append(str(course))
    all_genders = ["Undisclosed", "Male", "Female", "Other"]
    if request.method == "POST":
        if "logout" in request.form:
            session["currentuser"] = ""
            return redirect(url_for("signin"))
        if "settings" in request.form:
            return redirect(url_for("settings"))
        if "home" in request.form:
            return redirect(url_for("home"))
        if "search" in request.form:
            return redirect(url_for("search"))
        if "help" in request.form:
            return redirect(url_for("help"))
        if "uploadimage" in request.form:
            uploaded_file = request.files["profileicon"]
            if uploaded_file.filename != "":
                uploaded_file.save(r"project/static/assets/uploaded-profile-user.png")
                st_link.blob(f"icons/{userid}.png").upload_from_filename("project/static/assets/uploaded-profile-user.png")
                return redirect(url_for("home"))
        if "saveprofile" in request.form:
            save_profile(request.form["profilename"], request.form["profilegender"], request.form["profileaboutme"], request.form["profileinterests"], 
                request.form["profilefacebook"], request.form["profiletwitter"], request.form["profileinstagram"])
            return redirect(url_for("home"))
        if "savecourses" in request.form:
            save_courses(request.form.getlist("courseselection"))
            return redirect(url_for("home"))
        if "savestrengths" in request.form:
            save_strengths(request.form.getlist("strengthselection"))
            return redirect(url_for("home"))
        if "viewprofile" in request.form:
            return redirect(url_for("profile", inputtedid = session["currentuser"]))
        if "changepassword" in request.form:
            return redirect(url_for("changepassword"))
    return render_template("settings.html", name = profile_data["name"], zid = userid, aboutme = profile_data["aboutMe"], 
        gender = profile_data["gender"], genderlist = all_genders, facebook = profile_data["facebook"], interests = profile_data["interests"], 
        twitter = profile_data["twitter"], instagram = profile_data["instagram"], courselist = sorted(course_data), enrolled = enrolledcourses,
        strengthlist = sorted(strength_data), userstrengths = acknowledgedstrengths, backgroundimage = background_generator())

# COMPLETE - CHANGE PASSWORD
@app.route("/changepassword", methods=["GET", "POST"])
def changepassword():
    if session["currentuser"] == "":
        return redirect(url_for("error", reasoncode = "900", previouspage = "signin"))
    update_icon()
    profile_data_grab = fs_link.collection("profiles").document(session["currentuser"]).get()
    if profile_data_grab.exists:
        profile_data = profile_data_grab.to_dict()
    if request.method == "POST":
        if "logout" in request.form:
            session["currentuser"] = ""
            return redirect(url_for("signin"))
        if "settings" in request.form:
            return redirect(url_for("settings"))
        if "home" in request.form:
            return redirect(url_for("home"))
        if "search" in request.form:
            return redirect(url_for("search"))
        if "help" in request.form:
            return redirect(url_for("help"))
        if "cancel" in request.form:
            return redirect(url_for("settings"))
        if "changepassword" in request.form:
            originalpassword = request.form["oldpassword"]
            newpassword = request.form["newpassword"]
            confirmedpassword = request.form["confirmpassword"]
            credentials_grab = fs_link.collection("credentials").document(session["currentuser"]).get()
            if credentials_grab.exists:
                credentials_dict = credentials_grab.to_dict()
            if credentials_dict["password"] != originalpassword:
                return redirect(url_for("error", reasoncode = "100", previouspage = "changepassword"))
            if check_password_strength(newpassword) == False:
                return redirect(url_for("error", reasoncode = "202", previouspage = "changepassword"))
            if confirmedpassword != newpassword:
                return redirect(url_for("error", reasoncode = "203", previouspage = "changepassword"))
            save_password(newpassword)
            return redirect(url_for("settings"))
    return render_template("changepassword.html", name = profile_data["name"], zid = session["currentuser"],  backgroundimage = background_generator())

# COMPLETE - SEARCH
@app.route("/search", methods=["GET", "POST"])
def search():
    if session["currentuser"] == "":
        return redirect(url_for("error", reasoncode = "900", previouspage = "signin"))
    update_icon()
    profile_data_grab = fs_link.collection("profiles").document(session["currentuser"]).get()
    if profile_data_grab.exists:
        profile_data = profile_data_grab.to_dict()
    course_data_grab = fs_link.collection("other").document("courses").get()
    if course_data_grab.exists:
        course_data = course_data_grab.to_dict()["courses"]
    strength_data_grab = fs_link.collection("other").document("strengths").get()
    if strength_data_grab.exists:
        strength_data = strength_data_grab.to_dict()["strengths"]
    course_data_grab = fs_link.collection("other").document("courses").get()
    if course_data_grab.exists:
        course_data = course_data_grab.to_dict()["courses"]
    strength_data_grab = fs_link.collection("other").document("strengths").get()
    if strength_data_grab.exists:
        strength_data = strength_data_grab.to_dict()["strengths"]
    acknowledgedstrengths = []
    for strength in strength_data:
        if strength_data_grab.to_dict()["strengths"][strength]["students"].count(session["currentuser"]) > 0:
            acknowledgedstrengths.append(str(strength))
    enrolledcourses = []
    for course in course_data:
        if course_data_grab.to_dict()["courses"][course]["students"].count(session["currentuser"]) > 0:
            enrolledcourses.append(str(course))
    if request.method == "POST":
        if "logout" in request.form:
            session["currentuser"] = ""
            return redirect(url_for("signin"))
        if "settings" in request.form:
            return redirect(url_for("settings"))
        if "home" in request.form:
            return redirect(url_for("home"))
        if "search" in request.form:
            return redirect(url_for("search"))
        if "help" in request.form:
            return redirect(url_for("help"))
        if "searchbyid" in request.form:
            return redirect(url_for("profile", inputtedid = request.form["zidinput"]))
        if "searchbycourse" in request.form:
            if len(request.form.getlist("courseselection")) > 0:
                filter_students_courses(request.form.getlist("courseselection"))
                session["filtertype"] = "course"
                session["filtercriteria"] = request.form.getlist("courseselection")
                return redirect(url_for("results"))
        if "searchbystrength" in request.form:
            if len(request.form.getlist("strengthselection")) > 0:
                filter_students_strengths(request.form.getlist("strengthselection"))
                session["filtertype"] = "strength"
                session["filtercriteria"] = request.form.getlist("strengthselection")
                return redirect(url_for("results"))
    return render_template("search.html", name = profile_data["name"], zid = session["currentuser"], courselist = sorted(course_data), 
        strengthlist = sorted(strength_data), usercourses = enrolledcourses, userstrengths = acknowledgedstrengths, backgroundimage = background_generator())

# COMPLETE - RESULTS
@app.route("/search/results", methods=["GET", "POST"])
def results():
    if session["currentuser"] == "":
        return redirect(url_for("error", reasoncode = "900", previouspage = "signin"))
    update_icon()
    profile_data_grab = fs_link.collection("profiles").document(session["currentuser"]).get()
    if profile_data_grab.exists:
        profile_data = profile_data_grab.to_dict()
    if request.method == "POST":
        if "logout" in request.form:
            session["currentuser"] = ""
            return redirect(url_for("signin"))
        if "settings" in request.form:
            return redirect(url_for("settings"))
        if "home" in request.form:
            return redirect(url_for("home"))
        if "search" in request.form:
            return redirect(url_for("search"))
        if "help" in request.form:
            return redirect(url_for("help"))
        if "viewprofile" in request.form:
            return redirect(url_for("profile", inputtedid = request.form["studentredirect"]))
    return render_template("results.html", name = profile_data["name"], zid = session["currentuser"], filtertype = session["filtertype"], resultcriteria = session["filtercriteria"], studentlist = session["filterstudentlist"], backgroundimage = background_generator())

# COMPLETE - PROFILE
@app.route("/profile/<inputtedid>", methods=["GET", "POST"])
def profile(inputtedid):
    if session["currentuser"] == "":
        return redirect(url_for("error", reasoncode = "900", previouspage = "signin"))
    update_icon()
    profile_data_grab = fs_link.collection("profiles").document(session["currentuser"]).get()
    if profile_data_grab.exists:
        profile_data = profile_data_grab.to_dict()
    student_data_grab = fs_link.collection("profiles").document(inputtedid).get()
    if student_data_grab.exists:
        student_data = student_data_grab.to_dict()
    student_data["icon"] = st_link.blob(f"icons/{inputtedid}.png").generate_signed_url(datetime.timedelta(seconds=300), method='GET')
    course_data_grab = fs_link.collection("other").document("courses").get()
    if course_data_grab.exists:
        course_data = course_data_grab.to_dict()["courses"]
    strength_data_grab = fs_link.collection("other").document("strengths").get()
    if strength_data_grab.exists:
        strength_data = strength_data_grab.to_dict()["strengths"]
    acknowledgedstrengths = []
    for strength in strength_data:
        if strength_data_grab.to_dict()["strengths"][strength]["students"].count(inputtedid) > 0:
            acknowledgedstrengths.append(str(strength))
    enrolledcourses = []
    for course in course_data:
        if course_data_grab.to_dict()["courses"][course]["students"].count(inputtedid) > 0:
            enrolledcourses.append(str(course))
    if request.method == "POST":
        if "logout" in request.form:
            session["currentuser"] = ""
            return redirect(url_for("signin"))
        if "settings" in request.form:
            return redirect(url_for("settings"))
        if "home" in request.form:
            return redirect(url_for("home"))
        if "search" in request.form:
            return redirect(url_for("search"))
        if "help" in request.form:
            return redirect(url_for("help"))
    return render_template("profile.html", name = profile_data["name"], zid = session["currentuser"], studentid = inputtedid, 
        studentprofile = student_data, strengthlist = acknowledgedstrengths, courselist = enrolledcourses, backgroundimage = background_generator())

# COMPLETE - ERROR PAGE
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

# COMPLETE - RANDOM URL PAGE
@app.route("/<randomurl>", methods=["GET", "POST"])
def nothingfound(randomurl):
    if request.method == "POST":
        return redirect(url_for("signin"))
    return render_template("randomurl.html", url = randomurl)

if __name__ == "__main__":
    app.run(debug=True)