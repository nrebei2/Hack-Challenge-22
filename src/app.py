from db import db
from flask import Flask, request
import users_dao
import datetime

import json
import os

app = Flask(__name__)
db_filename = "journal.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


def extract_token(request):
    """
    Helper function that extracts the token from the header of a request
    """
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return False, failure_response("Missing authorization header", 400)

    bearer_token = auth_header.replace("Bearer ", "").strip()
    if bearer_token is None or not bearer_token:
        return False, failure_response("Invalid authorization header", 400)

    return True, bearer_token


@app.route("/")
def base_endpoint():
    return os.environ.get("NETID") + " was here!"


@app.route("/register/", methods=["POST"])
def register_account():
    """
    Endpoint for registering a new user
    """
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")

    if email is None or password is None:
        return failure_response("Missing email or password", 400)

    success, user = users_dao.create_user(email, password)

    if not success:
        return failure_response("User already exists", 400)

    return success_response(
        {
            "session_token": user.session_token,
            "session_expiration": str(user.session_expiration),
            "update_token": user.update_token
        }
    )


@app.route("/login/", methods=["POST"])
def login():
    """
    Endpoint for logging in a user
    """
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")

    if email is None or password is None:
        return failure_response("Missing email or password!", 400)

    success, user = users_dao.verify_credentials(email, password)

    if not success: 
        return failure_response("Incorrect email or password", 401)

    return success_response(
        {
            "session_token": user.session_token,
            "session_expiration": str(user.session_expiration),
            "update_token": user.update_token
        }
    )


@app.route("/session/", methods=["POST"])
def update_session():
    """
    Endpoint for updating a user's session
    """
    success, update_token = extract_token(request)

    if not success:
        return failure_response("Could not extract update token", 400)

    success_user, user = users_dao.renew_session(update_token)

    if not success_user:
        return failure_response("Invalid update token")

    return success_response({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token
    })


@app.route("/secret/", methods=["GET"])
def secret_message():
    """
    Endpoint for verifying a session token and returning a secret message

    In your project, you will use the same logic for any endpoint that needs 
    authentication
    """
    success, session_token = extract_token(request)

    if not success:
        return failure_response("Could not extract session token", 400)

    user = users_dao.get_user_by_session_token(session_token)
    if user is None or not user.verify_session_token(session_token):
        return failure_response("Invalid session token", 400)

    # handle logic of the endpoint
    # e.g. editing their profile

    return success_response({"message": "You have successfully implemented sessions!"})


@app.route("/logout/", methods=["POST"])
def logout():
    """
    Endpoint for logging out a user
    """
    success, session_token = extract_token(request)

    if not success:
        return failure_response("Could not extract session token", 400)

    user = users_dao.get_user_by_session_token(session_token)
    if user is None or not user.verify_session_token(session_token):
        return failure_response("Invalid session token", 400)

    user.session_token = ""
    user.session_expiration = datetime.datetime.now()
    user.update_token = ""
    db.session.commit()

    return success_response({"message": "You have successfully logged out"})

# --------------------------------------------
#  Entry routes
# --------------------------------------------

@app.route("/api/entries/")
def get_entry():
    entries = [entry.serialize() for entry in Entry.query.all()]
    return success_response({"entries": entries})

@app.route("/api/entries/", methods=["POST"])
def create_entry():
    '''
    Creates a new entry given a title, content, and emotion
    '''
    body = json.loads(request.data)

    title = body.get("title", None)
    content = body.get("content", None)
    emotion = body.get("emotion", None)

    success, session_token = extract_token(request)

    if not success:
        return failure_response("Could not extract session token", 400)

    user = users_dao.get_user_by_session_token(session_token)
    if user is None or not user.verify_session_token(session_token):
        return failure_response("Invalid session token", 400)

    if None in [title, content]:
        return failure_response("You either forgot to supply a title or content!", 400)
    
    if not emotion:
        return failure_response("You forgot to supply an emotion!", 400)

    new_entry = Entry(
        title=title,
        content=content,
        user=user.id,
        emotion=emotion
    )

    db.session.add(new_entry)
    db.session.commit()

    return success_response(new_entry.serialize(), 201)


@app.route("/api/entries/<int:id>/")
def get_entry(id):
    '''
    Retrieves entry given id
    '''
    entry = Entry.query.filter_by(id=id).first()
    if entry is None:
        return failure_response("entry not found!")
    return success_response(entry.serialize())


@app.route("/api/entries/<int:id>/", methods=["DELETE"])
def delete_entry(id):
    '''
    Delete entry given id
    '''
    entry = Entry.query.filter_by(id=id).first()
    if entry is None:
        return failure_response("entry not found!")
    db.session.delete(entry)
    db.session.commit()
    return success_response(entry.serialize())



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)