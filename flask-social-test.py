#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Michal Szczepanski'

import os
import logging
import logging.config
import dependencies
from datetime import datetime

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# MAIL
from flask_mail import Mail

#SECURITY
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, \
    login_required, login_user

# SOCIAL
from flask.ext.social import Social, login_failed
from flask.ext.social.views import connect_handler
from flask.ext.social.utils import get_connection_values_from_oauth_response
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore

# ADMIN
from flask_admin.contrib import sqla
import flask_admin as admin

def init_logging(directory):
    # check log directory exists
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except:
            raise RuntimeError('Cannot create directory for logs : %s' % directory)
    # load logging configuration

    logging.config.fileConfig('conf/logging.ini', defaults={
        'logdirectory': directory
    })


# APP WITH EXTENSIONS.

app = Flask(__name__)
app.config.from_object('config')

mail = Mail(app)

db = SQLAlchemy(app)

# DATABASE
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String)
    display_name = db.Column(db.String)
    full_name = db.Column(db.String)
    image_url = db.Column(db.String)
    profile_url = db.Column(db.String)
    provider_id = db.Column(db.String)
    provider_user_id = db.Column(db.String)
    secret = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('users', lazy='dynamic'))


# ADMIN
class RoleAdmin(sqla.ModelView):
    column_display_pk = True
    form_columns = ['id', 'name', 'description']


class UserAdmin(sqla.ModelView):
    column_display_pk = True
    form_columns = ['id', 'email', 'password', 'active', 'confirmed_at', 'roles']

class ConnectionAdmin(sqla.ModelView):
    column_display_pk = True
    form_columns = ['id',
                    'access_token',
                    'display_name',
                    'full_name',
                    'image_url',
                    'profile_url',
                    'provider_id',
                    'provider_user_id',
                    'secret',
                    'user_id']

# Create admin
admin = admin.Admin(app, name='Example: SQLAlchemy2', template_mode='bootstrap3')
admin.add_view(RoleAdmin(Role, db.session))
admin.add_view(UserAdmin(User, db.session))
admin.add_view(ConnectionAdmin(Connection, db.session))


security_ds = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, security_ds)
social_ds = SQLAlchemyConnectionDatastore(db, Connection)
social = Social(app, social_ds)

app.security = security
app.social = social

# Create tables at first request
@app.before_first_request
def create_user():
    db.create_all()

# Register when no such user - supports twitter / facebook
@login_failed.connect_via(app)
def on_login_failed(sender, provider, oauth_response):
    connection_values = get_connection_values_from_oauth_response(provider, oauth_response)
    provider_id = connection_values.get('provider_id')
    if provider_id is 'facebook':
        import facebook
        api = facebook.GraphAPI(access_token=oauth_response.get('access_token'))
        user_data = api.get_object(connection_values.get('provider_user_id'))
        ds = security.datastore
        user = ds.create_user(
            email=user_data.get('email'),
            active=True,
            confirmed_at=datetime.now()
        )
        ds.commit()
        connection_values['user_id'] = user.id
        connect_handler(connection_values, provider)
        if login_user(user):
            ds.commit()
            return render_template('index.html')
    elif provider_id is 'twitter':
        import twitter
        api = twitter.Api(consumer_key=provider.consumer_key,
                          consumer_secret=provider.consumer_secret,
                          access_token_key=connection_values.get('access_token'),
                          access_token_secret=connection_values.get('secret'))
        data = api.VerifyCredentials()
        ds = security.datastore
        twitter_display  = connection_values.get('display_name')
        user = ds.create_user(
            email='twitter{}'.format(twitter_display),
            active=True,
            confirmed_at=datetime.now()
        )
        ds.commit()
        connection_values['user_id'] = user.id
        connect_handler(connection_values, provider)
        if login_user(user):
            ds.commit()
            return redirect(url_for('index'))
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/test')
@login_required
def test():
    render_template('test.html')

@app.route('/profile')
@login_required
def profile():
    return render_template(
        'profile.html',
        content='Profile Page',
        facebook_conn=social.facebook.get_connection()
    )

if __name__ == '__main__':
    init_logging('logs')
    dependencies.download('static/ext', 'conf/html.json')
    app.run(use_reloader=False)
