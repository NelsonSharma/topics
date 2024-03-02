
#%%
__doc__=""" 
topics - Flask based web app for sharing files 
https://github.com/NelsonSharma/topics
Author: Nelson.S
"""
__version__="2.3.24"
def version(): return __version__
if __name__!='__main__':
    from sys import exit
    exit()
































#%% [0]
# ------------------------------------------------------------------------------------------
# parse arguments
# ------------------------------------------------------------------------------------------
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--topic',          type=str,       default='tOpIcS',          help='the main topic/subject')
parser.add_argument('--login',          type=str,       default='__login__.xlsx',  help='login excel file')
parser.add_argument('--case',           type=int,       default=0,                 help='convert uid to upper or lower case (-1 means lower-case, 1 means upper-case) (0 means as it is) ')
parser.add_argument('--ext',            type=str,       default='',                help='csv string of allowed file extensions, keep blank to allow all')
parser.add_argument('--maxupcount',     type=int,       default=0,                 help='maximum number of files that can be uploaded - keep 0 for no limit')
parser.add_argument('--maxupsize',      type=float,     default=0.0,               help='maximum size (in MB) of file that can be uploaded - keep 0 for no limit')
parser.add_argument('--port',           type=int,       default=8080,              help='port to host web server')
parser.add_argument('--host',           type=str,       default='',                help='ip-address to host web server, leave blank to server on all IPs - same as 0.0.0.0')
parser.add_argument('--uploads',        type=str,       default='__uploads__',     help='uploads folder')
parser.add_argument('--downloads',      type=str,       default='__downloads__',   help='downloads folder')
parser.add_argument('--verbose',        type=int,       default=1,                 help='verbose level 0=silent, 1=events, 2=detailed, 3 or more=detailed with timestamp')
args = parser.parse_args()
# ------------------------------------------------------------------------------------------
# imports ----------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
import platform, re, os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, abort, send_file
from flask_wtf import FlaskForm
from wtforms import SubmitField, MultipleFileField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
from waitress import serve
from math import inf
import datetime
now = datetime.datetime.now
# ------------------------------------------------------------------------------------------
# verbose levels
# ------------------------------------------------------------------------------------------
if args.verbose==0:
    def xprint(msg): pass
    def dprint(msg): pass
elif args.verbose==1:
    def xprint(msg): pass
    def dprint(msg): print(f'[{now()}] :: {msg}' )
elif args.verbose==2:
    def xprint(msg): print(msg)
    def dprint(msg): print(f'[{now()}] :: {msg}' )
else:
    def xprint(msg): print(f'[{now()}] :: {msg}' )
    def dprint(msg): print(f'[{now()}] :: {msg}' )
# ------------------------------------------------------------------------------------------

































#%% [1]
# ------------------------------------------------------------------------------------------
# WEB-SERVER INFORMATION
# ------------------------------------------------------------------------------------------
HOST_ALIAS =        f'{os.getlogin()} @ {platform.node()}:{platform.system()}.{platform.release()}'
APP_SECRET_KEY =    HOST_ALIAS
HOST_IP =           args.host if args.host else '0.0.0.0'           # use "0.0.0.0" to listen on all interfaces
HOST_PORT =         args.port                                       # use 8080 by default
xprint(f'Alias: {HOST_ALIAS}\nEndpoint: {HOST_IP}:{HOST_PORT}')
# ------------------------------------------------------------------------------------------
































#%% [2]
"""NOTE : reading login information 
    > read login info from an excel (.xlsx) file using pd.read_excel
    > `LOGIN_XL` contain excel file-name 
    > the sheet should have 4 cols -> [ ADMIN  UID  NAME  PASS ]
    
    > the `UID` field is the unique-id used to login
    > only those uids that are populated in the `UID` field of the login excel file will be allowed to login and use the app
    > one should pre-fill the `UID` field with known users

    > the `NAME` field represents full name - should be prefiled along with `UID`

    > the `PASS` field is the password for login
    > its initially kept blank - keeping it blank allows for the user to set password
    > this simulates the first-time login

    > the 'ADMIN' field indicates if the user is admin or not
    > admin can refresh downloads and persist db using 0.0.0.0:8080/x url
    > keeping it blank would mean that the user is not an admin
    > refreshing downloads is nessesary because simply adding files to the downloads folder will not reflect on app
    > persisting db is nessesary because a crash may cause loss on password for new users
    > reloading db is nessesary so that new users can be added without stopping the server


    > NOTE - 
        ~> at least one record must be entered so that when pandas reads this excel it knows what data-type is expected in each col
        ~> add a dummy record in the login sheet to hint at data-types
            specially with the `PASS` coloumn
            otherwise pandas will interpret `PASS` coloumn as float data-type
        ~> so a default admin user is created on the first run if login file is absent
"""

# ------------------------------------------------------------------------------------------
# LOGIN DATABASE - EXCEL
# ------------------------------------------------------------------------------------------
LOGIN_XL = args.login   # excel file that contains login information
LOGIN_XL_PATH = os.path.join( os.path.abspath(os.path.dirname(__file__)), LOGIN_XL) 
if not os.path.isfile(LOGIN_XL_PATH): 
    xprint(f'Login file {LOGIN_XL_PATH} not found - creating new...')
    db_dict = { #<---------------- default login file
        'ADMIN': [f'+'], #<---- any non blank string will work
        'UID': [f'{os.getlogin()}'],
        'NAME': [f'{platform.node()}'],
        'PASS': [''],
        }
    db_frame = pd.DataFrame( db_dict )
    for si in ['ADMIN', 'UID', 'NAME', 'PASS']: db_frame[si] = db_frame[si].astype(object)
    #xprint(f'Created New db\n{db_frame}\n')
    db_frame.to_excel(LOGIN_XL_PATH, sheet_name="login", index=False) # save updated login information to excel sheet
    del db_dict, db_frame
    xprint(f'Created new login file {LOGIN_XL_PATH}')
# ------------------------------------------------------------------------------------------
def read_db_from_disk():
    db_frame = pd.read_excel(LOGIN_XL_PATH) #<---- reading an invalid excel file may throw error - to be handled by user
    for si in ['ADMIN', 'UID', 'NAME', 'PASS']: db_frame[si] = db_frame[si].astype(object)
    #xprint(f'Loaded db\n{db_frame}\n')
    xprint(f'Loaded login file @ {LOGIN_XL_PATH}')
    return db_frame
# ------------------------------------------------------------------------------------------
def write_db_to_disk(db_frame): 
    try:
        db_frame.to_excel(LOGIN_XL_PATH, sheet_name="login", index=False) # save updated login information to excel sheet
        xprint(f'Persisted login file {LOGIN_XL_PATH}')
        return True
    except PermissionError:
        dprint(f'PermissionError - {LOGIN_XL_PATH} might be open, close it first.')
        return False
    
# ------------------------------------------------------------------------------------------
db = read_db_from_disk()  #<----------- Created db here 
# ------------------------------------------------------------------------------------------
































#%% [3]  
# settings and meta-info 

# ------------------------------------------------------------------------------------------
# displayed information 
# ------------------------------------------------------------------------------------------
HEADING_TEXT =          args.topic                  # usually the class/subject name
WELCOME_TEXT =          'Login to continue'         # text above login box shown at home-page
LOGIN_FAIL_TEXT =       'Login failed'              # text information when login fails
LOGIN_CREATE_TEXT =     'Password created'          # text information when new password is created
LOGIN_CASE =            args.case
# ------------------------------------------------------------------------------------------
# password policy
# ------------------------------------------------------------------------------------------
MIN_PASSWORD_LEN = 1            # minimum password length that can be set by users
INVALID_PASSWORD_WARN = f'Password should be atleast {MIN_PASSWORD_LEN} char(s) - can use alphabets, numbers, underscore and @-symbol' # a warning msg to be displayed when incorrect password is created
def VALIDATE_PASSWORD(password):   # a function that can validate the password - returns bool type
    try:
        assert len(password) >= MIN_PASSWORD_LEN
        assert len(re.findall("[a-zA-Z]|[0-9]|_|@", password)) == len(password)
        return True
    except AssertionError: return False
# ------------------------------------------------------------------------------------------
# upload settings
# ------------------------------------------------------------------------------------------
UPLOAD_FOLDER = args.uploads           # this is with respect to current script (__file__) - files are uploaded under each users folder
UPLOAD_FOLDER_PATH = os.path.join( os.path.abspath(os.path.dirname(__file__)), UPLOAD_FOLDER) 
os.makedirs(UPLOAD_FOLDER_PATH, exist_ok=True)
xprint(f'Upload Folder: {UPLOAD_FOLDER} @ {UPLOAD_FOLDER_PATH}')
ALLOWED_EXTENSIONS = set([]) if not args.ext else set(args.ext.split(','))  # a set or list of file extensions that are allowed to be uploaded e.g - {'txt', 'py', 'zip', 'jpg', 'mp4'}
def VALIDATE_EXTENSION(filename):   # a function that checks for valid file extensions based on ALLOWED_EXTENSIONS
    if len(ALLOWED_EXTENSIONS): return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    else: return True
KB = 2**10
MB = 2**20                                        # 1 MB in bytes
GB = 2**30
TB = 2**40
MAX_UPLOAD_SIZE = abs(args.maxupsize*MB)  if args.maxupsize else TB       # maximum upload file size 
MAX_UPLOAD_COUNT = abs(args.maxupcount) if args.maxupcount else inf        # maximum number of files that can be uploaded by one user
INITIAL_UPLOAD_STATUS = []           # a list of notes to be displayed to the users about uploading files
if ALLOWED_EXTENSIONS:  INITIAL_UPLOAD_STATUS.append((-1, f'allowed extensions:\t#[{len(ALLOWED_EXTENSIONS)}] {ALLOWED_EXTENSIONS}'))
else:                   INITIAL_UPLOAD_STATUS.append((-1, f'allowed extensions:\tany'))


# find max upload size in appropiate units
mus_kb = MAX_UPLOAD_SIZE/KB
if len(f'{int(mus_kb)}') < 4:
    mus_display = f'{mus_kb:.2f} KB'
else:
    mus_mb = MAX_UPLOAD_SIZE/MB
    if len(f'{int(mus_mb)}') < 4:
        mus_display = f'{mus_mb:.2f} MB'
    else:
        mus_gb = MAX_UPLOAD_SIZE/GB
        if len(f'{int(mus_gb)}') < 4:
            mus_display = f'{mus_gb:.2f} GB'
        else:
            mus_tb = MAX_UPLOAD_SIZE/TB
            mus_display = f'{mus_tb:.2f} TB'




INITIAL_UPLOAD_STATUS.append((-1, f'max file-size:\t{mus_display}'))
INITIAL_UPLOAD_STATUS.append((-1, f'max file-count:\t{MAX_UPLOAD_COUNT}'))

xprint(f'Upload Settings: {INITIAL_UPLOAD_STATUS}')
# ------------------------------------------------------------------------------------------
# download settings
# ------------------------------------------------------------------------------------------
DOWNLOAD_FOLDER = args.downloads       # this is with respect to current script (__file__) - represents the "resources" page
DOWNLOAD_FOLDER_PATH = os.path.join( os.path.abspath(os.path.dirname(__file__)), DOWNLOAD_FOLDER) 
os.makedirs(DOWNLOAD_FOLDER_PATH, exist_ok=True)
xprint(f'Download Folder: {DOWNLOAD_FOLDER} @ {DOWNLOAD_FOLDER_PATH}')
# a list of downloadable files - this is computed at the app startup - so newly added files will not be reflected untill restart
def GET_DOWNLOAD_FILE_LIST (): return [(f, os.path.join(DOWNLOAD_FOLDER_PATH, f)) for f in os.listdir(DOWNLOAD_FOLDER_PATH) if os.path.isfile(os.path.join(DOWNLOAD_FOLDER_PATH, f))]
DOWNLOAD_FILE_LIST = GET_DOWNLOAD_FILE_LIST()
xprint(f'Download filelist: {len(DOWNLOAD_FILE_LIST)} item(s)')
# ------------------------------------------------------------------------------------------
# application setting and instance
# ------------------------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key =                APP_SECRET_KEY
app.config['UPLOAD_FOLDER'] =   UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
class UploadFileForm(FlaskForm): # The upload form using FlaskForm
    file = MultipleFileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")
# HTML templates
TEMPLATE_LOGIN =    'login.html'
TEMPLATE_UPLOAD =     'upload.html'
TEMPLATE_DOWNLOAD = 'download.html'
# ------------------------------------------------------------------------------------------
































#%% [4]
# app.route  > all app.route implemented here 
# Analytical Data collection (ADC) variables defined as (adc_)

# ------------------------------------------------------------------------------------------
# login
# ------------------------------------------------------------------------------------------
adc_total_login_requests=0
adc_total_login_success=0
adc_total_login_failed=0
adc_total_login_create=0
adc_total_login_unknown=0
adc_total_hits = 0
adc_total_force_logouts=0
@app.route('/', methods =['GET', 'POST'])
def login():
    r""" the login page - if a user is already logged in -> 
        redirects to `upload` page on get request 
        force login on post method - this will force logout existung user if its different from the new one that is trying to login
        """
    global adc_total_login_requests, adc_total_login_success, adc_total_login_failed, adc_total_login_create, adc_total_login_unknown, adc_total_hits
    if request.method == 'POST' and 'uid' in request.form and 'passwd' in request.form:
        in_uid = f"{request.form['uid']}"
        in_passwd = f"{request.form['passwd']}"
        #xprint(f"[.] some trying to login using [ {in_uid} | {in_passwd} ]")
        adc_total_login_requests+=1
        in_query = in_uid if not LOGIN_CASE else (in_uid.upper() if LOGIN_CASE>0 else in_uid.lower())
        xprint(f"[.] login attempt by [{in_uid}] will case-query [{in_query}]")

        try:                record = db.query("UID==@in_query")
        except KeyError:    record = None
        if not len(record): record=None
        xprint(f"[...] record matched? [{record is not None}]")
        if record is not None: 
            passwd = record['PASS'].values[0]
            named = record['NAME'].values[0]
            uid = record['UID'].values[0]
            admind = record['ADMIN'].values[0]
            #print(f'{passwd=}, {named=}, {uid=}, {admind=}')
            xprint(f"[....] matched record [{uid}|{named}]")
            if pd.isnull(passwd) or passwd=='': # fist login
                xprint(f"[---------] first login")
                if in_passwd: # new password provided
                    #xprint(f"[---------] new password provided [{in_passwd}]")
                    if VALIDATE_PASSWORD(in_passwd): # new password is valid
                        #xprint(f"[---------] new password is valid")  
                        record['PASS'].values[0]=in_passwd
                        db.update(record)
                        xprint(f'[---------] updated record') # \n{record}
                        msg = LOGIN_CREATE_TEXT
                        heading = HEADING_TEXT
                        warn = f'[{in_uid}] New password was created successfully'
                        dprint(f'{named} just joined')
                        adc_total_login_create+=1
                                               
                    else: # new password is invalid valid
                        #xprint(f"[........] new password is invalid")  
                        msg = LOGIN_FAIL_TEXT
                        warn=f'[{in_uid}] New password is invalid - {INVALID_PASSWORD_WARN}'
                        heading=HEADING_TEXT
                        
                                               
                else: #new password not provided       
                    #xprint(f"[.....] new password was not provided")             
                    msg = LOGIN_FAIL_TEXT
                    heading=HEADING_TEXT
                    warn = f'[{in_uid}] New password must be created before logging in'
                                           
            else: # re login
                xprint(f"[........] revist login")
                if in_passwd: # password provided
                    #xprint(f"[........] password provided {in_passwd}")  
                    if in_passwd==passwd:
                        #xprint(f"[......] password does match") 
                        folder_name = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], uid) 
                        #xprint(f"user {session['uid']} landed on upload page")
                        try:
                            os.makedirs(folder_name, exist_ok=True)
                            #xprint(f"..... has directory {folder_name}")
                        except:
                            xprint(f'[!] Directory could not be created @ {folder_name} :: Force logout user {uid}')
                            adc_total_force_logouts+=1
                            return redirect(url_for('logout'))
                    
                        session['has_login'] = True
                        session['uid'] = uid
                        session['named'] = named
                        session['admind'] = admind
                        session['filed'] = os.listdir(folder_name)
                        xprint(f'[........] login Success {uid}|{named}')
                        dprint(f'{session["named"]} has logged in') 
                        #xprint(f"filed @ login= {session['filed']}")
                        adc_total_login_success+=1


                    
                        return redirect(url_for('upload'))
                    else:  
                        #xprint(f"[.....] password does not match")  
                        msg = LOGIN_FAIL_TEXT
                        heading=HEADING_TEXT
                        warn = f'[{in_uid}] Password mismatch'
                        adc_total_login_failed+=1
                                                 
                else: # password not provided
                    #xprint(f"[....] password not provided")  
                    msg = LOGIN_FAIL_TEXT
                    heading=HEADING_TEXT
                    warn = f'[{in_uid}] Password not provided'
                    adc_total_login_failed+=1
        else:
            xprint(f"[....] unmatched record {in_uid}")
            msg = LOGIN_FAIL_TEXT
            heading=HEADING_TEXT
            warn = f'[{in_uid}] Not a valid user'
            adc_total_login_unknown+=1
                                    
    else:
        
        if session.get('has_login', False): 
            #xprint(f"++page hit was redirected for {session['uid']}")
            return redirect(url_for('upload'))
        adc_total_hits+=1
        xprint(f"[+] page hit [{adc_total_hits}]")
        msg = WELCOME_TEXT
        heading = HEADING_TEXT
        warn = f'Hosted by {HOST_ALIAS}'
        
    
    return render_template(TEMPLATE_LOGIN, msg = msg, heading = heading, warn = warn)
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# logout
# ------------------------------------------------------------------------------------------
adc_total_logouts=0
@app.route('/logout')
def logout():
    r""" logout a user and redirect to login page """
    global adc_total_logouts
    xprint(f"[-] log out user {session['uid']}")
    dprint(f'{session["named"]} is logging out') 
    session['has_login'] = False
    session['uid'] = ""
    session['named'] = ""
    session['admind'] = ""
    session['filed'] = []
    adc_total_logouts+=1
    return redirect(url_for('login'))
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# download
# ------------------------------------------------------------------------------------------
adc_total_downloads_requests = 0
adc_total_downloads_success = 0
adc_total_downloads_failed = 0
@app.route('/download', methods =['GET'], defaults={'req_path': ''})
@app.route('/download/<path:req_path>')
def download(req_path):
    r""" the resources page - 
        displays a list of downloadable resources and allows downloading using GET method 
        the files are listed from `DOWNLOAD_FOLDER`
    """
    global adc_total_downloads_requests, adc_total_downloads_failed, adc_total_downloads_success
    if not session.get('has_login', False): return redirect(url_for('login'))
    abs_path = os.path.join(DOWNLOAD_FOLDER_PATH, req_path) # Joining the base and the requested path
    if req_path:
        xprint(f"[_] {session['uid']} trying to download {req_path}")
        adc_total_downloads_requests+=1
    if not os.path.exists(abs_path): 
        xprint(f" ... requested file was not found")
        adc_total_downloads_failed+=1
        return abort(404) # Return 404 if path doesn't exist
    if os.path.isfile(abs_path): 
        xprint(f" ... sending file ")
        dprint(f'{session["named"]} just downloaded the file {req_path}')
        adc_total_downloads_success+=1
        return send_file(abs_path) # Check if path is a file and serve
    return render_template(TEMPLATE_DOWNLOAD, filelist = DOWNLOAD_FILE_LIST, heading=HEADING_TEXT)
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# upload
# ------------------------------------------------------------------------------------------
adc_total_files_uploaded=0
adc_total_files_upload_failed=0
@app.route('/upload', methods =['GET', 'POST'])
def upload():
    r""" homepage of users - after they login 
    - this is where the file upload is available to the users """
    global adc_total_files_uploaded, adc_total_files_upload_failed
    if not session.get('has_login', False): return redirect(url_for('login'))
    form = UploadFileForm()
    folder_name = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                app.config['UPLOAD_FOLDER'],
                session['uid']) 
    #xprint(f"user {session['uid']} landed on upload page")    
    #xprint(f"..... has uploaded {len(file_list)} items")

    if form.validate_on_submit():
        xprint(f"user {session['uid']} is trying to upload {len(form.file.data)} items.")
        result = []
        adc_total_files_upload_failed += len(form.file.data)
        n_success = 0
        #---------------------------------------------------------------------------------
        for file in form.file.data:
            #xprint(f"[...........] {file.filename}")
        #---------------------------------------------------------------------------------
            if not VALIDATE_EXTENSION(file.filename):
                why_failed = f"FAILURE :: Extension is invalid [{file.filename}] "
                result.append((0, why_failed))
                continue

            file_name = os.path.join(folder_name, secure_filename(file.filename))
            if not os.path.exists(file_name):
                #file_list = os.listdir(folder_name)
                if len(session['filed'])>=MAX_UPLOAD_COUNT:
                    why_failed = f"FAILURE :: Upload limit reached [{file.filename}] "
                    result.append((0, why_failed))
                    continue


            file.save(file_name) 
            why_failed = f"SUCCESS :: Uploaded new file [{file.filename}] "
            result.append((1, why_failed))
            n_success+=1
            session['filed']= session['filed'] + [file.filename]
            adc_total_files_uploaded+=1
            adc_total_files_upload_failed-=1
            
            
            
        #---------------------------------------------------------------------------------
        
        xprint(f"upload results: \n{result}")
        dprint(f'{session["named"]} just uploaded {n_success} file(s)') 
        file_list = session['filed'] #os.listdir(folder_name)
        msg = f'You have uploaded {len(file_list)} file(s)'  
        return render_template(TEMPLATE_UPLOAD, form=form, msg=msg, heading=HEADING_TEXT, filelist=file_list, status=result)
        
    file_list = session['filed'] #os.listdir(folder_name)
    #dprint(f"filed @ get-upload = {session['filed']}")
    msg = f'You have uploaded {len(file_list)} file(s)'  
    return render_template(TEMPLATE_UPLOAD, form=form, msg=msg, heading=HEADING_TEXT, filelist=file_list, status=INITIAL_UPLOAD_STATUS)
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# purge
# ------------------------------------------------------------------------------------------
adc_total_purged=0
adc_total_files_purged=0
@app.route('/purge', methods =['GET'])
def purge():
    r""" purges all files that a user has uploaded in their respective uplaod directory
    NOTE: each user will have its won directory, so choose usernames such that a corresponding folder name is a valid one
    """
    global adc_total_purged, adc_total_files_purged
    if not session.get('has_login', False): return redirect(url_for('login'))
    folder_name = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                app.config['UPLOAD_FOLDER'],
                session['uid']) 
    if os.path.exists(folder_name):
        file_list = os.listdir(folder_name)
        for f in file_list: os.remove(os.path.join(folder_name, f))
        xprint(f"{session['uid']} has purged their files.")
        dprint(f'{session["named"]} used purge')
        session['filed']=[]
        #dprint(f"filed @ purge= {session['filed']}")
        adc_total_purged+=1
        adc_total_files_purged+=len(file_list)
    return redirect(url_for('upload'))
# ------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------
# administrative
# ------------------------------------------------------------------------------------------
FAILED_ADMIN_MSG = "[FAILURE] :: This action requires admin privilege"
@app.route('/ref', methods =['GET']) 
def refresh_dll():
    r""" refreshes the  DOWNLOAD_FILE_LIST"""
    global DOWNLOAD_FILE_LIST, GET_DOWNLOAD_FILE_LIST
    if not session.get('has_login', False): return redirect(url_for('login')) # "Not Allowed - Requires Login"
    if not pd.isnull(session['admind']): 
        DOWNLOAD_FILE_LIST = GET_DOWNLOAD_FILE_LIST()
        dprint(f"[@] {session['uid']} just refreshed the download list.")
        return "[SUCCESS] :: download-list was refreshed"
    else: return FAILED_ADMIN_MSG
@app.route('/dbw', methods =['GET']) 
def persist_db():
    r""" writes db to disk """
    global db, write_db_to_disk
    if not session.get('has_login', False): return redirect(url_for('login')) # "Not Allowed - Requires Login"
    if not pd.isnull(session['admind']): 
        if write_db_to_disk(db):
            dprint(f"[@] {session['uid']} just persisted the db to disk.")
            return "[SUCCESS] :: db written to disk"
        else: return f"[ERROR] :: {LOGIN_XL} might be open, close it first."
    else: return FAILED_ADMIN_MSG
@app.route('/dbr', methods =['GET']) # rdb for reload db
def reload_db():
    r""" reloads db from disk """
    global db, read_db_from_disk
    if not session.get('has_login', False): return redirect(url_for('login')) # "Not Allowed - Requires Login"
    if not pd.isnull(session['admind']): 
        db = read_db_from_disk()
        dprint(f"[@] {session['uid']} just reloaded the db from disk.")
        return "[SUCCESS] :: db reloaded from disk"
    else: return FAILED_ADMIN_MSG
# ------------------------------------------------------------------------------------------
































#%% [5]
# main --> server start

octates = [ bool(int(x)) for x in HOST_IP.split('.') ]
display_HOST_IP = HOST_IP if True in octates else "localhost"
dprint(f'running topics version: {version()}')
dprint(f'starting server @ {HOST_IP}:{HOST_PORT} \n\thttp://{display_HOST_IP}:{HOST_PORT}\n\thttp://{display_HOST_IP}:{HOST_PORT}/ref\n\thttp://{display_HOST_IP}:{HOST_PORT}/dbr\n\thttp://{display_HOST_IP}:{HOST_PORT}/dbw')

start_time = now()
serve(app, host=HOST_IP, port=HOST_PORT, max_request_body_size=MAX_UPLOAD_SIZE) 
# start serving app at this ip --> to stop app - use ctrl+c
stop_time = now()
dprint(f'stopping server...')
while not write_db_to_disk(db):
    t = input('Press Enter to try again')
    if t: 
        dprint(f'could not persist db to {LOGIN_XL_PATH}')
        break
xprint('done! total up-time was {}'.format(stop_time-start_time))
#-----------------------------------------------------------------------
print(f"""
ADC stats:
---------------------------------------
Logins
---------------------------------------
{adc_total_login_requests=}
{adc_total_login_success=}
{adc_total_login_failed=}
{adc_total_login_create=}
{adc_total_login_unknown=}
{adc_total_hits=}
---------------------------------------
Logouts
---------------------------------------
{adc_total_force_logouts=}
{adc_total_logouts=}
---------------------------------------
Downloads
---------------------------------------
{adc_total_downloads_requests=}
{adc_total_downloads_success=}
{adc_total_downloads_failed=}
---------------------------------------
Uploads
---------------------------------------
{adc_total_files_uploaded=}
{adc_total_files_upload_failed=}
---------------------------------------
Purges
---------------------------------------
{adc_total_purged=}
{adc_total_files_purged=}
---------------------------------------
""")
# ------------------------------------------------------------------------------------------
#%% [6]
# ------------------------------------------------------------------------------------------
""" FOOTNOTE 

"""
# ------------------------------------------------------------------------------------------