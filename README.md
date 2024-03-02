# 📤 . . . *topics* . . . 📥

Flask-based web app for sharing files

---

## setup *topics* to run on your machine

### [0] clone repo and cd into it

```bash
git clone https://github.com/NelsonSharma/topics.git
cd topics
```

### [1] create a virtual environment

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

### [3] start the app

start the app server by launching `app.py`

```bash
python app.py 
```

use ctrl+c to stop the server

### [4] (optional) start with extra arguments

```cmd
python app.py --topic="my topic" --login="my login.xlsx" --case=0 --ext="txt,jpeg,jpeg,mp4,zip" --maxupcount=10 --maxupsize=256 --port=8080 --host=127.0.0.1 --uploads="my uploads" --downloads="my downloads" --verbose=2
```

Description of Arguments

```python

--topic         
# name of the topic - this is displayed as the main heading at the top of all pages

--login         
# name of login database file - an Excel file stored in the current dir 
# default is "__login__.xlsx" (will auto-create if not found)

--case          
# convert uid to upper or lower case 
# [-1] means lower-case, [1] means upper-case, [0] means no convert
# default is [0] which means no convert

--ext           
# allowed file extensions that can be uploaded (expects a CSV-string)
# default is empty-string which means any file is allowed

--maxupcount    
# max no. of files that a user can upload
# default is [0] which means no-limit

--maxupsize     
# max file-size (in MB) that can be uploaded 
# (actually represent the `max_request_body_size` argument in `waitress.serve`)
# default is [0] which means 1 TB

--port          
# port of server ip-endpoint 
# default is 8080

--host          
# address of server ip-endpoint 
# default is empty-string which means use all interfaces

--uploads       
# name of folder used to store uploaded files
# default is "__uploads__"

--downloads     
# name of the folder used to serve files as resources
# default is "__downloads__"

--verbose       
# verbose level 
# (0=silent), (1=events), (2=detailed), (>2=detailed with timestamp)
# default is [1]

```

Note: the `--case` argument is to convert the uid entered by users to either upper-case or lower-case.

For example, if uids are case insensitive but are stored in upper-case in the login database,
then specifying `--case=1` will allow the uid entered by the user to be converted to upper-case before
querying to the login database. This way users don't necessarily have to capitalize their uid at the time of login.
Otherwise, the login might fail since uids are case sensitive i.e., `--case=0` by default.

---

## where are the files?

* files placed in the default `__downloads__` folder will be available for download (only top-level files)
* files uploaded by external users will be stored in default `__uploads__/<uid>` folder
  * NOTE: since each user has its own directory with the same name as the uid of the user it is important to avoid illegal characters like backslash or slash in uids
  * if folder names do not support these characters, then the user's directory will not be created and they will always be auto-logged out

---

## note on login databse

Login databse is an excel (.xlsx) file.
At server start-up, login file is read once and stored into an in-memory dataframe called login-db ( the `db` variable in `app.py`)

Login file contains a "login" sheet that has 4 columns -> [ `ADMIN`  `UID`  `NAME`  `PASS` ]

* `UID` and `NAME`
  * the `UID` field is the unique-id used to login
  * only those uids that are populated in the `UID` field of the login file will be allowed to login and use the app
  * one should pre-fill the `UID` field with known users
  * the `NAME` field represents full name - should be pre-filed along with `UID`

* `PASS`
  * the `PASS` field contains user's password
  * its initially kept blank - keeping it blank allows for the user to set password when the login for the first time
  * to set new password, enter uid and the new password on the login page and click on `Login`
  * if the new password is valid, it will be created and a message will be displayed to user confirming the same

* `ADMIN`
  * the `ADMIN` field indicates if the user is an admin or not
  * keeping it blank would mean that the user is not an admin
  * an admin can refresh download-list, persist and reload login-db using `<ip>:<port>/<cmd>` url
  * a default admin user will be auto-created on the first run if the specified login file is absent

---

## how to admin?

* Adding/Removing/Updating Users
  * default login file `__login__.xlsx` will be created if not present or not specified otherwise
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
  * this is to avoid restarting the server to persist changes to disk

* Refreshing/Updating download list
  * files can be placed inside the `__downloads__` folder to be shared
  * when the server is started, it prepares and stores a list of files available in the `__downloads__` folder
  * however, if new files are added to `__downloads__` folder, they will not reflect if the server is running already
  * it will be required to re-scan the `__downloads__` folder and rebuild the download-list
  * an admin user can do so by going to the `<ip>:<port>/ref` url
  * this is to avoid restarting the server to update the download list

---

> *topics* verision: 2.3.24
>
> author: `mail.nelsonsharma@gmail.com`

---
