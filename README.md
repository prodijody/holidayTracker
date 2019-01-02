## Getting started (Windows 10)

### Create a virtual env first in any folder and activate it
In the prompt cmd:
```
(cmd) virtualenv c:/desktop/path/to/folder/
(cmd) cd c:/path/to/folder/Scripts
(cmd) activate
```

### Clone the repo and install requirments
```
(venv) clone https://github.com/j-000/holidayTracker
(venv) pip install -r requirements
```

### Create your config file with the following python dicts
This is for a gmail account. You will need to [allow less secure](https://myaccount.google.com/lesssecureapps?pli=1) apps to be able to send email through the app.
```
mail_settings = {
  'MAIL_USERNAME' : 'your email',
  'MAIL_PASSWORD' : 'your password',
  'MAIL_DEFAULT_SENDER' : 'your email again'
}

app_settings = {
'SQLALCHEMY_DATABASE_URI' : 'sqlite:///data.db',
'SECRET_KEY' : 'some very secret string',
'SECURITY_PASSWORD_SALT' : 'some secret hash as well'
}

admin_user = {
    'NAME' : 'your name',
    'SURNAME' : 'your surname',
    'EMAIL' : 'your email',
    'APP_PASSWORD':'some password',
    'HOLIDAYS_QUOTA' : 30
}

random_string = {
    '_' : 'aiodjaiosdjaiodjaiodjaiosdjioasdjaiodj'
}
```

save the file as **config_file.py**.

### Start Python shell and create DB
This will populate the db with your User account that has your email and password to login into the app.
```
(venv) python
>>> from helperFunctions import restartDB
>>> restartDB()
>>> exit()
```

### Run it
```
(venv) python app.py
 Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 123-456-789
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
