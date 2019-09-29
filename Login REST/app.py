import re
import os
from models import User, UserSchema, app, db
from datetime import date, datetime
from validate_email import validate_email
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


app = app
db = db
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

user_Schema = UserSchema()
users_Schema = UserSchema(many=True)


@app.route('/api/create', methods=["POST"])

def create():
    if request.method == "POST":
        f_name = request.json.get('first_name')
        l_name = request.json.get('last_name')
        c_code = request.json.get('country_code')
        p_number = request.json.get('phone_number')
        gender_ = request.json.get('gender')
        bday = request.json.get('birthday')
        avatar_ = request.json.get('avatar')
        mail = request.json.get('email')

        if f_name is "":
            return (jsonify({ "first_name":  { "error": "blank" }}),400, {'Location': url_for('create', _external=True)} )

        if l_name is "":
            return (jsonify({ "last_name":  { "error": "blank" }}),400, {'Location': url_for('create', _external=True)} )

        if c_code != "EG":
            return (jsonify({ "country_code": { "error": "inclusion" } }),400, {'Location': url_for('create', _external=True)} )

        pattern = '01[0-2](\d{8})'
        phone_match = re.match(pattern, p_number)
        if not phone_match :
            return (jsonify({ "phone_number": [ { "error": "blank" }, { "error": "not_a_number" },
                                { "error":"not_exist" }, { "error": "invalid" },
                                { "error": "taken" }, { "error": "too_short", "count": 10 },
                                { "error":"too_long", "count": 15 } ]}),
                                400, {'Location': url_for('create', _external=True)} )
        if gender_ not in  ["female", 'male', 'other'] :
            return (jsonify({ "gender": [ { "error": "inclusion" } ]}),400, {'Location': url_for('create', _external=True)} )



        if bday is "":
            return (jsonify({ "birthdate": [ { "error": "blank" },{ "error": "in_the_future" } ]}),
                    400, {'Location': url_for('create', _external=True)} )
        else:
            try:
                if bday != datetime.strptime(bday, "%Y-%m-%d").strftime('%Y-%m-%d'):
                    raise ValueError
            except ValueError:
                return (jsonify({ "birthdate": [ { "error": "blank" },{ "error": "in_the_future" } ]}),
                        400, {'Location': url_for('create', _external=True)} )


        avatar_extention = avatar_.split(".")[1]
        if avatar_extention not in ['jpg', 'jpeg', 'png'] or avatar_ is "" :
            return (jsonify({"avatar": [ { "error": "blank" }, { "error": "invalid_content_type" } ]}),400, {'Location': url_for('create', _external=True)} )


        mail_valid = validate_email(mail)
        all_users = User.query.all()
        taken_mail = False
        for u in all_users:
            if u.email == mail:
                taken_mail = True
                break
        if not mail_valid or taken_mail:
            return (jsonify({ "email": [{ "error": "taken" }, { "error": "invalid" } ]}),
                    400, {'Location': url_for('create', _external=True)} )



        new_user = User(first_name=f_name, last_name=l_name,
            country_code=c_code, phone_number=p_number, gender= gender_, birthday=bday, avatar=avatar_, email=mail)
        db.session.add(new_user)
        db.session.commit()
        #return user_Schema.jsonify(new_user)
        return (user_Schema.jsonify(new_user),
         201,
            {'Location': url_for('get_User_by_id', id=new_user.id, _external=True)})



@app.route('/api/user/<int:id>', methods=['GET'])
def get_User_by_id(id):
    user_id = User.query.get(id)
    result = user_Schema.dump(user_id)
    return jsonify(result)

@app.route('/api/users', methods=['GET'])
def get_all_users():
    all_users = User.query.all()
    result = users_Schema.dump(all_users)
    return jsonify(result)


@app.route('/api/user/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    f_name = request.json.get('first_name')
    l_name = request.json.get('last_name')
    c_code = request.json.get('country_code')
    p_number = request.json.get('phone_number')
    gender_ = request.json.get('gender')
    bday = request.json.get('birthday')
    avatar_ = request.json.get('avatar')
    mail = request.json.get('email')


    user.first_name = f_name
    user.last_name = l_name
    user.country_code = c_code
    user.phone_number = p_number
    user.gender = gender_
    user.birthday = bday
    user.avatar = avatar_
    user.email = mail
    db.session.commit()

    return user_Schema.jsonify(user)

@app.route('/api/delete/<int:id>', methods=['DELETE'])
def delete_user(id):
    user_id = User.query.get(id)

    all_users = User.query.all()

    if user_id :
        db.session.delete(user_id)
        db.session.commit()
        return users_Schema.jsonify(all_users)

    return( "User with id = " + id + " not found to be deleted")

@app.route('/api/delete/all', methods=['DELETE'])
def delete_all_users():
    all_users = User.query.all()
    for user in all_users:
        db.session.delete(user)

    db.session.commit()
    return users_Schema.jsonify(all_users)


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True, port=5000)
