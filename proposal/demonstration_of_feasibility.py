import firebase_admin
import time
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("other-files\miniprofiles-801b3-firebase-adminsdk-a02t1-8cb3692aa2.json")
firebase_admin.initialize_app(cred)

database_connection = firestore.client()

signed_in = False
current_user = ""
profile_sections = ["name","gender","about-me"]
loop_program = True

print("-----------------------------")
print("Sample IDs are as follows:")
print("zID      z1234567    z7654321")
print("Password password123 321password")
print("DoB      01/01/2021  31/12/2021")

def view_profile():
    target_id = input("Whose profile would you like to check out? ")
    get_profile = database_connection.collection('profiles').document(target_id).get()
    if get_profile.exists:
        profile_contents_dict = get_profile.to_dict()
        print("><><><><><><><><><")
        for section in profile_sections:
            print(profile_contents_dict[section])
        print("><><><><><><><><><")
    else:
        print("No profile / user could be found.")

def edit_profile(section):
    if profile_sections.count(section) > 0:
        updated_value = input("What do you want to replace it with? ")
        database_connection.collection('profiles').document(current_user).update({section: updated_value})
        print("Success!")
    else:
        print("Can't edit an unknown section!")

while loop_program:
    print("-----------------------------")
    if signed_in == False:
        zid_input = input("What is your zID? Or alternatively, type *END* to end the program. ")
        actual_password = ""
        actual_dob = ""
        if zid_input == "*END*":
            loop_program = False
        else:
            get_credentials = database_connection.collection('credentials').document(zid_input).get()
            if get_credentials.exists:
                verify_cred_dict = get_credentials.to_dict()
                actual_password = str(verify_cred_dict["password"])
                actual_dob = str(verify_cred_dict["dob"])
                password_input = input("What is your password? ")
                dob_input = input("What is your date of birth (00/00/0000 notation)? ")
                if password_input != actual_password or dob_input != actual_dob:
                    signed_in = False
                    current_user = ""
                    print("Sign in failed.")
                else:
                    signed_in = True
                    current_user = zid_input
                    print("Sign in succeeded.")
            else:
                signed_in = False
                current_user = ""
                print("Your zID doesn't exist ont the system.")
    else:
        print("Signed in as: " + current_user)
        print("Commands: logout, view or edit")
        check_command = input("What do you want to do? ")
        if check_command == "logout":
            signed_in = False
            current_user = ""
        elif check_command == "view":
            view_profile()
        elif check_command == "edit":
            edit_commands = ""
            for section in profile_sections:
                edit_commands += section + ", "
            print("You can edit: " + edit_commands)
            edit_what = input("What would you like to edit? ")
            edit_profile(edit_what)
        else:
            print("Error: Unknown Command")
            print("Please try again.")