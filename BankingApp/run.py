# app.py
from app import create_app
from flask import redirect, url_for

app = create_app()

@app.route("/")
def index():
    # Redirect to login or dashboard, depending on your preference.
    return redirect(url_for("auth.login"))

if __name__ == '__main__':
    app.run(debug=True)
