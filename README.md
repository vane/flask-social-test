#Login using flask-social example

Using sqlite database for simplicity<br />
Included flask-admin to see database structure<br />
all files are in flask-social-test.py file<br />
provides auto registration code with facebook/twitter<br />

###Connected providers
1. facebook
<br />
```
pip install http://github.com/pythonforfacebook/facebook-sdk/tarball/master
```
2. twitter
<br />
```
pip install python-twitter
```

### Setup
1. copy/move config.py.template as config.py
2. fill SOCIAL_FACEBOOK, SOCIAL_TWITTER with api keys

### Run
1. commandline type:
<br />
```
python flask-social-test.py
```
2. go to [http://localhost:5000/](http://localhost:5000/)

###to use twitter:
1. go to [https://apps.twitter.com/](https://apps.twitter.com/)
2. create app and get "consumer key" and "consumer secret" from "Keys and Access Tokens" tab
3. set callback url to http://127.0.0.1:5000/login/twitter
4. mark checkbox "Allow this application to be used to Sign in with Twitter"
5. click update

###to use facebook
1. go to [https://developers.facebook.com/apps/](https://developers.facebook.com/apps/)
2. create app
3. go to "Settings" tab menu
4. get "App ID" and "App Secret" fill it as "consumer_key" and "consumer_secret"
5. Add platform -> Website and type http://localhost:5000/ as url  

#### Troubleshoting
1. don't go to 127.0.0.1:5000 cause facebook won't authorize you
2. don't bother messages look at [http://localhost:5000/admin/connection/](http://localhost:5000/admin/connection/) 
to check everything is ok  