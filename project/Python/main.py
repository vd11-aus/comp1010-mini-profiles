from flask import *
from pyhtml import html, h1, p, form, input_, br

app = Flask("__name__")

@app.route('/', methods=["GET","POST"])
def main_menu():
    if request.method == "POST":
        url = ""
        if "view_student" in request.form:
            url = "view_student"
        elif "search_by_class" in request.form:
            url = "search_by_class"
        elif "create_account" in request.form:
            url = "create_account"
        elif "sign_in" in request.form:
            url = "sign_in"
        return redirect(url_for(url))
    visual_html = html(
        h1("Menu"),
        form(
            input_(type = "submit", name = "view_student", value = "View Student"),
            br,
            input_(type = "submit", name = "search_by_class", value = "Search by Class"),
            br,
            input_(type = "submit", name = "create_account", value = "Create Account"),
            br,
            input_(type = "submit", name = "sign_in", value = "Sign In")
        )
    )
    return str(visual_html)

@app.route('/findbyid', methods=["GET","POST"])
def view_student():
    visual_html = html(
        h1("Find By ID"),
    )
    return str(visual_html)

@app.route('/searchbyclass', methods=["GET","POST"])
def search_by_class():
    visual_html = html(
        h1("Search By Class"),
    )
    return str(visual_html)

@app.route('/createaccount', methods=["GET","POST"])
def create_account():
    visual_html = html(
        h1("Create Account"),
    )
    return str(visual_html)

@app.route('/signin', methods=["GET","POST"])
def sign_in():
    visual_html = html(
        h1("Sign In"),
    )
    return str(visual_html)

if __name__ == "__main__":
    app.run(debug = True)