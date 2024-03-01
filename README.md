# 📤 . . . *topics* . . . 📥

Flask based web app for sharing files

---

## setup *topics* to run on your machine

### [0] clone repo and cd into it

```bash
git clone https://github.com/NelsonSharma/topics.git
cd topics
```

### [1] create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### [2] install required packages

```bash
python -m pip install pandas openpyxl Flask Flask-WTF waitress
```

or use

```bash
python -m pip install -r requirements.txt
```

### [3] launch app using `app.py`

```bash
python app.py  # use ctrl+c to stop the server 
```

### [4] (optional) launch with extra arguments

```bash
python app.py \
--topic="my topic" \
--login=mylogin.xlsx \
--case=0 \
--ext="txt,jpeg,jpeg,mp4,zip" \
--maxupfiles=10 \
--maxupsize=256 \
--port=8080 \
--host=127.0.0.1\
--verbose=0
```

---

## where are the files?

* files uploaded by external users will be stored in default `__uploads__/<uid>` folder
* files placed in default `__downloads__` folder will be available for download (only top-level files)
* default login file `__login__.xlsx` will be created if not present or not specified otherwise
* users can be added or removed directly in `__login__.xlsx`
* when adding new user, keeping the `PASS` field blank will enable users to set a password on the first login
* NOTE: since each user has its own directory with the same name as the uid of the user,
* it is important avoid illegal characters like backslash or slash in uids
* if folder-names do not support these characters, then user's directory will not be created and they will always be auto-logged out

---

## how to admin?

* Adding/Removing/Updating Users
    * users can be added or removed directly in `__login__.xlsx`
    * however, doing so will not be reflected in the app immediately if its running already
    * this requires the in-memory login-db (which is a dataframe) to be reloaded from `__login__.xlsx`
    * an admin user can do so by going to the `<ip>:<port>/dbr` url (dbr for db-read)
    * this is to avoid restarting the server to update the login-db

* Persisting login-database to disk manually
    * users that login first time will create new passwords
    * these passwords are again, stored in the in-memory login-db (which is a dataframe)
    * the changes will be persisted to disk when the server is stopped (using ctrl+c)
    * however, if the server crashes before that, then the new passwords will be lost
    * the in-memory login-db must be written back to `__login__.xlsx`
    * an admin user can do so by going to the `<ip>:<port>/dbw` url (dbw for db-write)
    * this is to avoid restarting the server to persist changes to disk and also, we would like to avoid writing to disk frequently

* Refreshing/Updating download list
    * files can be placed inside the `__downloads__` folder to be shared
    * when the server is started, it prepares and stores a list of files available in the `__downloads__` folder
    * however if new files are added to `__downloads__` folder, they will not reflect immediately if the server is running
    * it will be required to re-scan the `__downloads__` folder and rebuild the list
    * an admin user can do so by going to the `<ip>:<port>/ref` url
    * this is to avoid restarting the server to update the download list

---

## Note from author

* *topics* is an extremely lightweight app. It does not include any security features. 
* It uses a simple excel file to store user's login credentials. 
* It is meant to be used in a somewhat controlled environment and should not be used in a production.
* Any suggestions and contributions to *topics* are welcomed.

---

Author: Nelson.S (mail.nelsonsharma@gmail.com)

---

