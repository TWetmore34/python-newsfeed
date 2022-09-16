from flask import Blueprint, request, jsonify, session
from app.models import User
from app.db import get_db
import sys

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/users', methods=['POST'])
def signup():
    data = request.get_json()
    db = get_db()

    try:
        newUser = User(
            username = data['username'],
            email = data['email'],
            password = data['password']
        )

        db.add(newUser)
        db.commit()
    except:
        # print error msg
        print(sys.exc_info()[0])
        db.rollback()
        return jsonify(message = 'signup failed'), 500

    # create session
    session.clear()
    session['user_id'] = newUser.id
    session['loggedIn'] = True

    return jsonify(id = newUser.id), 200

@bp.route('/users/logout', methods=['POST'])
def logout():
    session.clear()
    return '', 204

@bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    db = get_db()

    try:
        user = user = db.query(User).filter(User.email == data['email']).one()
    except:
        print(sys.exc_info()[0])
        return jsonify(message = 'User not found')
    
    # bcrypt compare?
    if user.verify_password(data['password']) == False:
        return jsonify(message = 'Incorrect username or password'), 400
    
    session.clear()
    session['user_id'] = user.id
    session['loggedIn'] = True

    return jsonify(id = user.id), 200