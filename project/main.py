from flask import *
from pyhtml import html, h1, p, form, input_, br

app = Flask("__name__")

@app.route('/', methods=["GET","POST"])
def main_menu():
    if request.method == "POST":
        return redirect(url_for("view_student"))
    visual_html = html(
        h1("Menu"),
        form(
            input_(type = "submit", name = "view_student", value = "View Student"),
            br,
            input_(type = "submit", name = "search_by_class", value = "Search by Class"),
            br,
            input_(type = "submit", name = "create_profile", value = "Create Profile"),
            br,
            input_(type = "submit", name = "edit_existing", value = "Edit Existing Profile"),
        )
    )
    return str(visual_html)

@app.route('/findbyid', methods=["GET","POST"])
def view_student():
    visual_html = html(
        h1("WHEASDE"),
    )
    return str(visual_html)

if __name__ == "__main__":
    app.run(debug = True)