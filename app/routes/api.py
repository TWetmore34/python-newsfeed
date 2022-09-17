from email import message
from flask import Blueprint, request, jsonify, session
from app.models import User, Post, Comment, Vote
from app.db import get_db
import sys
from app.utils.auth import login_required

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
    
    if user.verify_password(data['password']) == False:
        return jsonify(message = 'Incorrect username or password'), 400
    
    session.clear()
    session['user_id'] = user.id
    session['loggedIn'] = True

    return jsonify(id = user.id), 200

@bp.route('/comments', methods=['POST'])
@login_required

def comment():
    data = request.get_json()
    db = get_db()

    try:
        newComment = Comment(
            comment_text = data['comment_text'],
            user_id = session.get('user_id'),
            post_id = data['post_id']
        )

        db.add(newComment)
        db.commit()

        return jsonify(id = newComment.id)
    except:
        print(sys.exc_info()[0])

        db.rollback()
        return jsonify(message = 'Comment failed')

# handle upvotes
@bp.route('/posts/upvote', methods=['PUT'])
@login_required

def upvote():
    data = request.get_json()
    db = get_db()
    # add limit to one upvote per person
    try:
        upvote = Vote(
            user_id = session.get('user_id'),
            post_id = data['post_id']
        )
        db.add(upvote)
        db.commit()

        return jsonify(message = 'upvote successful'), 204
    except:
        print(sys.exc_info()[0])

        db.rollback()
        return jsonify(message = 'Upvote failed'), 500

# create posts
@bp.route('/posts', methods=["POST"])
@login_required

def newPost():
    data = request.get_json()
    db = get_db()

    try:
        newPost = Post(
            title = data['title'],
            post_url = data['post_url'],
            user_id = session.get('user_id')
        )
        db.add(newPost)
        db.commit()
        
        return jsonify(id = newPost.id)

    except:
        print(sys.exc_info()[0])

        db.rollback()
        return jsonify(message = 'error posting')

# update post
@bp.route('/posts/<id>', methods=['PUT'])
@login_required

def updatePost(id):
    data = request.get_json()
    db = get_db()

    try:
        post = db.query(Post).filter(Post.id == id).one()
        post.title = data["title"]
        db.commit()

        return jsonify(message = 'post updated'), 204
    except:
        print(sys.exc_info()[0])

        db.rollback()
        return jsonify(message = 'update failed'), 500

@bp.route('posts/<id>', methods=['DELETE'])
@login_required

def delete(id):
    db = get_db()

    try:
        db.delete(db.query(Post).filter(Post.id == id).one())
        db.commit()

        return jsonify(message = 'deleted'), 204

    except:
        print(sys.exc_info()[0])

        db.rollback()
        return jsonify(message = 'delete failed'), 500