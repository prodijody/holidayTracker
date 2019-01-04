## Getting started (Windows 10)

##### 1) Clone the repo and install the requirements
Do this in a virtualenv folder, preferably. See [virtualenv for python](https://docs.python-guide.org/dev/virtualenvs/) for details.
```
(venv) clone https://github.com/j-000/holidayTracker
(venv) pip install -r requirements
```

##### 2) Create your config file with the following python dicts
**'mail_settings'** - works on gmail accounts only. You will need to [allow less secure apps](https://myaccount.google.com/lesssecureapps?pli=1) to be able to send email through the application.

**admin_user** - The email described in this dict will be the one used to send emails and alerts via the application.
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

save the file as **config_file.py** in the same directory as **app.py**.

##### 3) Start the Python shell in the terminal and initialize the database
This will populate the database with your User account.
```
(venv) python
>>> from helperFunctions import restartDB
>>> restartDB()
>>> exit()
```

##### 4) Run it and log in
```
(venv) python app.py
```
To login use the '**EMAIL**' and '**APP_PASSWORD**' details from the config file.

