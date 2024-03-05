#%%

# topics app 

#%%
__doc__=""" 
topics - Flask-based web app for sharing files 
https://github.com/NelsonSharma/topics
Author: Nelson.S
"""
__version__="2.3.24"
from sys import exit
if __name__!='__main__': exit()
class Fake:
    def __init__(self, **kwargs) -> None:
        for name, attribute in kwargs.items(): 
            try:setattr(self, name, attribute)
            except:pass
            
        

#%% [0]
VALID_ARGS = set([
    'base','secret','login','rename',
    'topic','emoji','welcome','case','ext','required','maxupcount','maxupsize',
    'port','host',
    'uploads','downloads','adc',
    'verbose'])
# ------------------------------------------------------------------------------------------
# parse arguments
# ------------------------------------------------------------------------------------------
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--config',         type=str,       default='',                help='all arguments in a config file - overrides everything')
parser.add_argument('--base',           type=str,       default='',                help='the base directory to host at')
parser.add_argument('--secret',         type=str,       default='__secret__.txt',  help='the app secret key - this is nessesary and constant through application lifecycle - helps manage sessions')
parser.add_argument('--login',          type=str,       default='__login__.xlsx',  help='login excel file')
parser.add_argument('--rename',         type=int,       default=0,                 help='allow updating user name field')
parser.add_argument('--topic',          type=str,       default='tOpIcS',          help='the main topic/subject')
parser.add_argument('--emoji',          type=str,       default='💻',              help='an emoji character to be displayed with uid and name')
parser.add_argument('--welcome',        type=str,       default='Welcome!',        help='welcome text on login page')
parser.add_argument('--case',           type=int,       default=0,                 help='convert uid to upper or lower case (-1 means lower-case, 1 means upper-case) (0 means as it is) ')
parser.add_argument('--ext',            type=str,       default='',                help='csv string of allowed file extensions, keep blank to allow all')
parser.add_argument('--required',       type=str,       default='',                help='cvs list of files required - overrides ext')
parser.add_argument('--maxupcount',     type=int,       default=0,                 help='maximum number of files that can be uploaded - keep 0 for no limit')
parser.add_argument('--maxupsize',      type=float,     default=0.0,               help='maximum size (in MB) of file that can be uploaded - keep 0 for no limit')
parser.add_argument('--port',           type=int,       default=8080,              help='port to host web server')
parser.add_argument('--host',           type=str,       default='',                help='ip-address to host web server, leave blank to server on all IPs - same as 0.0.0.0')
parser.add_argument('--uploads',        type=str,       default='__uploads__',     help='uploads folder')
parser.add_argument('--downloads',      type=str,       default='__downloads__',   help='downloads folder')
parser.add_argument('--adc',            type=str,       default='__adc__',         help='default dir to store adc (data)')
parser.add_argument('--verbose',        type=int,       default=0,                 help='verbose level - keep 0 for silent')
args = parser.parse_args()

if args.config: # override everything
    try:
        config_func_name = f'{args.config}'
        import importlib
        config_ = getattr(importlib.import_module("config") , config_func_name)()
        args = Fake(**config_)
    except: exit(f'error reading config @ {args.config}')

    for k in VALID_ARGS: 
        if not hasattr(args, k): exit(f'config is missing attribute {k}')

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
HOST_INFO = f'{os.getlogin()}@{platform.node()}' 
# ------------------------------------------------------------------------------------------
# verbose levels
# ------------------------------------------------------------------------------------------
if args.verbose==0:
    def xprint(msg): pass
    def dprint(msg): pass
elif args.verbose==1:
    def xprint(msg): pass
    def dprint(msg): print(msg)
elif args.verbose==2:
    def xprint(msg): pass
    def dprint(msg): print(f'[{now()}]\t{msg}' )
elif args.verbose==3:
    def xprint(msg): print(msg)
    def dprint(msg): print(f'[{now()}]\t{msg}' )
else:
    def xprint(msg): pass
    def dprint(msg): pass
# ------------------------------------------------------------------------------------------


#%% [1]
    
# Read base dir first 

BASEDIR = os.path.abspath((args.base if args.base else os.path.dirname(__file__)))
try:     os.makedirs(BASEDIR, exist_ok=True)
except:  exit(f'[!] base directory  @ {BASEDIR} was not found and could not be created') 
xprint(f'⚙ Base dicectiry:\t{BASEDIR}')
# ------------------------------------------------------------------------------------------
# WEB-SERVER INFORMATION
# ------------------------------------------------------------------------------------------\
if not args.secret: exit(f'secret key was not provided!')
APP_SECRET_KEY_FILE = os.path.join(BASEDIR, args.secret)
if not os.path.isfile(APP_SECRET_KEY_FILE): #< --- if key dont exist, create it
    APP_SECRET_KEY = '{}:{}'.format(HOST_INFO, now())
    try:
        with open(APP_SECRET_KEY_FILE, 'w') as f: f.write(APP_SECRET_KEY) #<---- auto-generated key
    except: exit(f'could not create secret key @ {APP_SECRET_KEY_FILE}')
    xprint(f'⇒ New secret created:\t{APP_SECRET_KEY_FILE}')
else:
    try:
        with open(APP_SECRET_KEY_FILE, 'r') as f: APP_SECRET_KEY = f.read()
        xprint(f'⇒ Load secret from:\t{APP_SECRET_KEY_FILE}')
    except: exit(f'could not read secret key @ {APP_SECRET_KEY_FILE}')


# ------------------------------------------------------------------------------------------


#%% [2]

# ------------------------------------------------------------------------------------------
# LOGIN DATABASE - EXCEL
# ------------------------------------------------------------------------------------------
if not args.login: exit(f'login file was not provided!')
LOGIN_XL_PATH = os.path.join( BASEDIR, args.login) 
if not os.path.isfile(LOGIN_XL_PATH): 
    xprint(f'⇒ Login file {LOGIN_XL_PATH} not found - creating new...')
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
    xprint(f'⇒ Created new login file:\t{LOGIN_XL_PATH}')
# ------------------------------------------------------------------------------------------
def read_db_from_disk():
    db_frame = pd.read_excel(LOGIN_XL_PATH, dtype=str, engine='openpyxl') #<---- reading an invalid excel file may throw error - to be handled by user
    for si in ['ADMIN', 'UID', 'NAME', 'PASS']: db_frame[si] = db_frame[si].astype(object)
    #xprint(f'Loaded db\n{db_frame}\n')
    xprint(f'⇒ Loaded login file:\t{LOGIN_XL_PATH}')
    return db_frame
# ------------------------------------------------------------------------------------------
def write_db_to_disk(db_frame): 
    try:
        db_frame.to_excel(LOGIN_XL_PATH, engine='openpyxl', sheet_name="login", index=False) # save updated login information to excel sheet
        xprint(f'⇒ Persisted login file:\t{LOGIN_XL_PATH}')
        app.config['pendingdb'] = 0
        return True
    except PermissionError:
        dprint(f'⇒ PermissionError - {LOGIN_XL_PATH} might be open, close it first.')
        return False
    
# ------------------------------------------------------------------------------------------
db = read_db_from_disk()  #<----------- Created db here 
# ------------------------------------------------------------------------------------------


#%% [3]  
# settings and meta-info 

# ------------------------------------------------------------------------------------------
# displayed information 
# ------------------------------------------------------------------------------------------
      
# ------------------------------------------------------------------------------------------
# password policy
# ------------------------------------------------------------------------------------------
def VALIDATE_PASSWORD(password):   # a function that can validate the password - returns bool type
    try:
        assert len(password) >= 1 # MIN_PASSWORD_LEN = 1 
        assert len(re.findall("[a-zA-Z]|[0-9]|_|@", password)) == len(password)
        return True
    except AssertionError: return False
# ------------------------------------------------------------------------------------------
# download settings
# ------------------------------------------------------------------------------------------
if not args.downloads: exit(f'downloads folder was not provided!')
DOWNLOAD_FOLDER_PATH = os.path.join( BASEDIR, args.downloads) 
try: os.makedirs(DOWNLOAD_FOLDER_PATH, exist_ok=True)
except: exit(f'downloads folder @ {DOWNLOAD_FOLDER_PATH} was not found and count not be created')
xprint(f'⚙ Download Folder:\t{DOWNLOAD_FOLDER_PATH}')
def GET_DOWNLOAD_FILE_LIST (): 
    dlist = []
    d = DOWNLOAD_FOLDER_PATH
    for f in os.listdir(d):
        p = os.path.join(d, f)
        if os.path.isfile(p): dlist.append(f)
    return dlist
DOWNLOAD_FILE_LIST = GET_DOWNLOAD_FILE_LIST()
xprint(f'⚙ Download filelist\t{len(DOWNLOAD_FILE_LIST)} item(s)')

# ------------------------------------------------------------------------------------------
# upload settings
# ------------------------------------------------------------------------------------------
if not args.uploads: exit(f'uploads folder was not provided!')
UPLOAD_FOLDER_PATH = os.path.join( BASEDIR, args.uploads ) 
try: os.makedirs(UPLOAD_FOLDER_PATH, exist_ok=True)
except: exit(f'uploads folder @ {UPLOAD_FOLDER_PATH} was not found and count not be created')
xprint(f'⚙ Upload Folder:\t{UPLOAD_FOLDER_PATH}')

ALLOWED_EXTENSIONS = set([x.strip() for x in args.ext.split(',') if x])  # a set or list of file extensions that are allowed to be uploaded 
if '' in ALLOWED_EXTENSIONS: ALLOWED_EXTENSIONS.remove('')
def get_valid_re_pattern(validext):
    if not validext: return ".+"
    pattern=""
    for e in validext: pattern+=f'{e}|'
    return pattern[:-1]
VALID_FILES_PATTERN = get_valid_re_pattern(ALLOWED_EXTENSIONS)

# def VALIDATE_EXTENSION(filename):   # a function that checks for valid file extensions based on ALLOWED_EXTENSIONS
#     if len(ALLOWED_EXTENSIONS): return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#     else: return True
REQUIRED_FILES = set([x.strip() for x in args.required.split(',') if x])  # a set or list of file extensions that are allowed to be uploaded 
if '' in REQUIRED_FILES: REQUIRED_FILES.remove('')

def VALIDATE_FILENAME(filename):   # a function that checks for valid file extensions based on ALLOWED_EXTENSIONS
    if '.' in filename: 
        name, ext = filename.rsplit('.', 1)
        if REQUIRED_FILES:  return f'{name}.{ext.lower()}' in REQUIRED_FILES
        else:               return bool(re.fullmatch(f'.+\.({VALID_FILES_PATTERN})$', f'{name}.{ext.lower()}'))
    else:               
        name, ext = filename, ''
        if REQUIRED_FILES:  return f'{name}' in REQUIRED_FILES
        else:               return not ALLOWED_EXTENSIONS


KB, MB, GB, TB = 2**10, 2**20, 2**30, 2**40
MAX_UPLOAD_SIZE = abs(args.maxupsize*MB)  if args.maxupsize else TB       # maximum upload file size 
MAX_UPLOAD_COUNT = abs(args.maxupcount) if args.maxupcount else inf        # maximum number of files that can be uploaded by one user

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

INITIAL_UPLOAD_STATUS = []           # a list of notes to be displayed to the users about uploading files
if REQUIRED_FILES:
    INITIAL_UPLOAD_STATUS.append((-1, f'accepted files [{len(REQUIRED_FILES)}]:\t{REQUIRED_FILES}'))
else:
    if ALLOWED_EXTENSIONS:  INITIAL_UPLOAD_STATUS.append((-1, f'allowed extensions [{len(ALLOWED_EXTENSIONS)}]:\t{ALLOWED_EXTENSIONS}'))
    #else:                   INITIAL_UPLOAD_STATUS.append((-1, f'allowed extensions:\tany'))
INITIAL_UPLOAD_STATUS.append((-1, f'max file-size:\t{mus_display}'))
if not (MAX_UPLOAD_COUNT is inf): INITIAL_UPLOAD_STATUS.append((-1, f'max file-count:\t{MAX_UPLOAD_COUNT}'))

xprint(f'⚙ Upload Settings:\n{INITIAL_UPLOAD_STATUS}')
# ------------------------------------------------------------------------------------------
# download settings
# ------------------------------------------------------------------------------------------



# ------------------------------------------------------------------------------------------
# application setting and instance
# ------------------------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key =          APP_SECRET_KEY
app.config['base'] =      BASEDIR
app.config['uploads'] =   UPLOAD_FOLDER_PATH
app.config['downloads'] = DOWNLOAD_FOLDER_PATH
app.config['emoji'] =     args.emoji
app.config['topic'] =     args.topic
app.config['hostinfo'] =  HOST_INFO
app.config['dfl'] = DOWNLOAD_FILE_LIST
app.config['rename'] = bool(args.rename)
app.config['pendingdb'] = 0
class UploadFileForm(FlaskForm): # The upload form using FlaskForm
    file = MultipleFileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")
# HTML templates




# ------------------------------------------------------------------------------------------


#%% [4]
# app.route  > all app.route implemented here 
# Analytical Data collection (ADC) variables defined as (adc_)

# ------------------------------------------------------------------------------------------
# login
# ------------------------------------------------------------------------------------------
adc_login = dict(
        requests=0,
        success=0,
        failed=0,
        create=0,
        unknown=0,
        hits=0,
        kicks=0,
        logouts=0,
)
@app.route('/', methods =['GET', 'POST'])
def login():
    LOGIN_NEED_TEXT =       '🔒'
    LOGIN_FAIL_TEXT =       '🔥'              
    LOGIN_CREATE_TEXT =     '🔑'    
    TEMPLATE_LOGIN =    'login.html'
    global adc_login
    if request.method == 'POST' and 'uid' in request.form and 'passwd' in request.form:
        in_uid = f"{request.form['uid']}"
        in_passwd = f"{request.form['passwd']}"
        in_name = f'{request.form["named"]}' if 'named' in request.form else ''
        adc_login['requests']+=1 #xprint(f"[.] some trying to login using [ {in_uid} | {in_passwd} ]")
        in_query = in_uid if not args.case else (in_uid.upper() if args.case>0 else in_uid.lower())
        xprint(f"◦ login attempt by [{in_uid}] will case-query [{in_query}]")

        try:                record = db.query("UID==@in_query")
        except KeyError:    record = None
        if not len(record): record=None
        xprint(f"◦ record matched? [{record is not None}]")
        if record is not None: 
            passwd = record['PASS'].values[0]
            named = record['NAME'].values[0]
            uid = record['UID'].values[0]
            admind = record['ADMIN'].values[0]
            if pd.isnull(admind): admind=''
            #print(f'{passwd=}, {named=}, {uid=}, {admind=}')
            xprint(f"◦ matched record [{uid}|{named}]")
            if pd.isnull(passwd) or passwd=='': # fist login
                xprint(f"◦ first login")
                if in_passwd: # new password provided
                    #xprint(f"[---------] new password provided [{in_passwd}]")
                    if VALIDATE_PASSWORD(in_passwd): # new password is valid
                        #xprint(f"[---------] new password is valid")  
                        record['PASS'].values[0]=in_passwd 
                        if in_name and in_name!=named and app.config['rename'] : 
                            record['NAME'].values[0]=in_name
                            named = in_name
                        db.update(record)
                        app.config['pendingdb']+=1
                        xprint(f'◦ updated record') # \n{record}

                        warn = LOGIN_CREATE_TEXT
                        msg = f'[{in_uid}.{named}] New password was created successfully'
                        dprint(f'● {in_uid}.{named} just joined')
                        adc_login['create']+=1
                                               
                    else: # new password is invalid valid
                        #xprint(f"[........] new password is invalid")  
                        warn = LOGIN_FAIL_TEXT
                        msg=f'[{in_uid}] New password is invalid - can use alpha-numeric, underscore and @-symbol'
                        
                                               
                else: #new password not provided       
                    #xprint(f"[.....] new password was not provided")             
                    warn = LOGIN_FAIL_TEXT
                    msg = f'[{in_uid}] New password required - can use alpha-numeric, underscore and @-symbol'
                                           
            else: # re login
                xprint(f"◦ revist login")
                if in_passwd: # password provided
                    #xprint(f"[........] password provided {in_passwd}")  
                    if in_passwd==passwd:
                        #xprint(f"[......] password does match") 
                        folder_name = os.path.join(app.config['uploads'], uid) 
                        #xprint(f"user {session['uid']} landed on upload page")
                        try:
                            os.makedirs(folder_name, exist_ok=True)
                            #xprint(f"..... has directory {folder_name}")
                        except:
                            xprint(f'◦ directory could not be created @ {folder_name} :: Force logout user {uid}')
                            session['has_login'] = False
                            session['uid'] = uid
                            session['named'] = named
                            adc_login['kicks']+=1
                            return redirect(url_for('logout'))
                    
                        session['has_login'] = True
                        session['uid'] = uid
                        session['admind'] = admind
                        session['filed'] = os.listdir(folder_name)
                        
                        if in_name and in_name!=named and app.config['rename']: 
                            session['named'] = in_name
                            record['NAME'].values[0]=in_name
                            db.update(record)
                            app.config['pendingdb']+=1
                            named = in_name
                            xprint(f'◦ updated record') # \n{record}
                        else: session['named'] = named

                        xprint(f'◦ login success {uid}|{named}')
                        dprint(f'● {session["uid"]}.{session["named"]} has logged in') 
                        #xprint(f"filed @ login= {session['filed']}")
                        adc_login['success']+=1

                        return redirect(url_for('upload'))
                    else:  
                        #xprint(f"[.....] password does not match")  
                        warn = LOGIN_FAIL_TEXT
                        msg = f'[{in_uid}] Password mismatch'
                        adc_login['failed']+=1
                                                 
                else: # password not provided
                    #xprint(f"[....] password not provided")  
                    warn = LOGIN_FAIL_TEXT
                    msg = f'[{in_uid}] Password not provided'
                    adc_login['failed']+=1
        else:
            xprint(f"◦ unmatched record {in_uid}")
            warn = LOGIN_FAIL_TEXT
            msg = f'[{in_uid}] Not a valid user'
            adc_login['unknown']+=1
                                    
    else:
        if session.get('has_login', False):  return redirect(url_for('upload'))
        
        adc_login['hits']+=1
        xprint(f"+ page hit [{adc_login['hits']}]")
        msg = args.welcome
        warn = LOGIN_NEED_TEXT 
        
    return render_template(TEMPLATE_LOGIN, msg = msg,  warn = warn)

@app.route('/logout')
def logout():
    r""" logout a user and redirect to login page """
    if not session.get('has_login', False):  return redirect(url_for('login'))
    if not session.get('uid', False): return redirect(url_for('login'))
    xprint(f"◦ log out user {session['uid']}")
    if session['has_login']:  dprint(f'● {session["uid"]}.{session["named"]} has logged out') 
    else: dprint(f'● {session["uid"]}.{session["named"]} was removed due to invalid uid ({session["uid"]})') 
    session['has_login'] = False
    session['uid'] = ""
    session['named'] = ""
    session['admind'] = ""
    session['filed'] = []
    global adc_login
    adc_login['logouts']+=1
    return redirect(url_for('login'))
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# download
# ------------------------------------------------------------------------------------------
adc_downloads = dict(
        requests=0,
        success=0,
        failed=0,
)
@app.route('/download', methods =['GET'], defaults={'req_path': ''})
@app.route('/download/<path:req_path>')
def download(req_path):
    TEMPLATE_DOWNLOAD = 'download.html'
    
    if not session.get('has_login', False): return redirect(url_for('login'))
    abs_path = os.path.join(app.config['downloads'], req_path) # Joining the base and the requested path
    global adc_downloads
    if req_path:
        xprint(f"◦ {session['uid']} trying to download {req_path}")
        adc_downloads['requests']+=1
    if not os.path.exists(abs_path): 
        xprint(f"◦ requested file was not found")
        adc_downloads['failed']+=1
        return abort(404) # Return 404 if path doesn't exist
    if os.path.isfile(abs_path): 
        xprint(f"◦ sending file ")
        dprint(f'● {session["uid"]}.{session["named"]} just downloaded the file {req_path}')
        adc_downloads['success']+=1
        return send_file(abs_path) # Check if path is a file and serve
    return render_template(TEMPLATE_DOWNLOAD)
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# upload
# ------------------------------------------------------------------------------------------
adc_uploads = dict(
        requests=0,
        success=0,
        failed=0,
)
@app.route('/upload', methods =['GET', 'POST'])
def upload():
    TEMPLATE_UPLOAD =   'upload.html'
    if not session.get('has_login', False): return redirect(url_for('login'))
    form = UploadFileForm()
    folder_name = os.path.join( app.config['uploads'], session['uid']) 
    #xprint(f"user {session['uid']} landed on upload page")    
    #xprint(f"..... has uploaded {len(file_list)} items")

    if form.validate_on_submit():
        
        global adc_uploads
        adc_uploads['requests']+=len(form.file.data)
        xprint(f"◦ user {session['uid']} is trying to upload {len(form.file.data)} items.")
        result = []
        n_success = 0
        #---------------------------------------------------------------------------------
        for file in form.file.data:
            sf = secure_filename(file.filename)
            #xprint(f"[...........] {file.filename} {sf}")
        #---------------------------------------------------------------------------------
            if not VALIDATE_FILENAME(sf):
                why_failed =  f"✗ File not accepted [{sf}] " if REQUIRED_FILES else f"✗ Extension is invalid [{sf}] "
                result.append((0, why_failed))
                adc_uploads['failed']+=1
                continue

            file_name = os.path.join(folder_name, sf)
            if not os.path.exists(file_name):
                #file_list = os.listdir(folder_name)
                if len(session['filed'])>=MAX_UPLOAD_COUNT:
                    why_failed = f"✗ Upload limit reached [{sf}] "
                    result.append((0, why_failed))
                    adc_uploads['failed']+=1
                    continue


            file.save(file_name) 
            why_failed = f"✓ Uploaded new file [{sf}] "
            result.append((1, why_failed))
            adc_uploads['success']+=1
            n_success+=1
            if sf not in session['filed']: session['filed'] = session['filed'] + [sf]

        #---------------------------------------------------------------------------------
        
        xprint(f"◦ upload results: \n{result}")
        dprint(f'● {session["uid"]}.{session["named"]} just uploaded {n_success} file(s)') 
        file_list = session['filed'] #os.listdir(folder_name)
        msg = f'You have uploaded {len(file_list)} file(s)'  
        return render_template(TEMPLATE_UPLOAD, form=form, msg=msg,  filelist=file_list, status=result)
        
    file_list = session['filed'] #os.listdir(folder_name)
    #dprint(f"filed @ get-upload = {session['filed']}")
    msg = f'You have uploaded {len(file_list)} file(s)'  
    return render_template(TEMPLATE_UPLOAD, form=form, msg=msg,  filelist=file_list, status=INITIAL_UPLOAD_STATUS)
# ------------------------------------------------------------------------------------------

@app.route('/uploadf', methods =['GET'])
def uploadf():
    r""" force upload - i.e., refresh by using os.list dir """
    if not session.get('has_login', False): return redirect(url_for('login'))
    folder_name = os.path.join( app.config['uploads'], session['uid']) 
    session['filed'] = os.listdir(folder_name)
    return redirect(url_for('upload'))

# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# purge
# ------------------------------------------------------------------------------------------
adc_purged = dict(requests=0, files=0)
@app.route('/purge', methods =['GET'])
def purge():
    r""" purges all files that a user has uploaded in their respective uplaod directory
    NOTE: each user will have its won directory, so choose usernames such that a corresponding folder name is a valid one
    """
    if not session.get('has_login', False): return redirect(url_for('login'))
    folder_name = os.path.join( app.config['uploads'], session['uid']) 
    if os.path.exists(folder_name):
        file_list = os.listdir(folder_name)
        for f in file_list: os.remove(os.path.join(folder_name, f))
        xprint(f"◦ {session['uid']} has purged their files.")
        dprint(f'● {session["uid"]}.{session["named"]} used purge')
        session['filed']=[]
        #dprint(f"filed @ purge= {session['filed']}")
        global adc_purged
        adc_purged['requests']+=1
        adc_purged['files']+=len(file_list)
    return redirect(url_for('upload'))
# ------------------------------------------------------------------------------------------

 
# ------------------------------------------------------------------------------------------
# administrative
# ------------------------------------------------------------------------------------------
FAILED_ADMIN_MSG = "This action requires admin privilege"
@app.route('/ref', methods =['GET']) 
def refresh_dll():
    r""" refreshes the  downloads"""
    if not session.get('has_login', False): return redirect(url_for('login')) # "Not Allowed - Requires Login"
    if session['admind']: 
        global GET_DOWNLOAD_FILE_LIST
        app.config['dfl'] = GET_DOWNLOAD_FILE_LIST()
        dprint(f"▶ {session['uid']}.{session['named']} just refreshed the download list.")
        STATUS, SUCCESS =  "Update download-list", True
    else: STATUS, SUCCESS =  FAILED_ADMIN_MSG, False
    TEMPLATE_ADMIN = 'admin.html'
    return render_template(TEMPLATE_ADMIN,  status=STATUS, success=SUCCESS)
@app.route('/dbw', methods =['GET']) 
def persist_db():
    r""" writes db to disk """
    if not session.get('has_login', False): return redirect(url_for('login')) # "Not Allowed - Requires Login"
    if session['admind']: 
        global db, write_db_to_disk
        if write_db_to_disk(db):
            dprint(f"▶ {session['uid']}.{session['named']} just persisted the db to disk.")
            STATUS, SUCCESS = "Persisted db to disk", True
        else: STATUS, SUCCESS =  f"Write error '{args.login}' might be open", False
    else: STATUS, SUCCESS =  FAILED_ADMIN_MSG, False
    TEMPLATE_ADMIN = 'admin.html'
    return render_template(TEMPLATE_ADMIN,  status=STATUS, success=SUCCESS)
@app.route('/dbr', methods =['GET']) # rdb for reload db
def reload_db():
    r""" reloads db from disk """
    if not session.get('has_login', False): return redirect(url_for('login')) # "Not Allowed - Requires Login"
    if session['admind']: 
        global db, read_db_from_disk
        db = read_db_from_disk()
        dprint(f"▶ {session['uid']}.{session['named']} just reloaded the db from disk.")
        STATUS, SUCCESS = "Reloaded db from disk", True
    else: STATUS, SUCCESS = FAILED_ADMIN_MSG, False
    TEMPLATE_ADMIN = 'admin.html'
    return render_template(TEMPLATE_ADMIN,  status=STATUS, success=SUCCESS)
# ------------------------------------------------------------------------------------------
@app.route('/admin', methods =['GET'])
def adminpage():
    r""" opens admin page """ 
    if not session.get('has_login', False): return redirect(url_for('login'))
    TEMPLATE_ADMIN = 'admin.html'
    if session['admind']: return render_template(TEMPLATE_ADMIN,  status="Admin Access", success=True)
    else: return render_template(TEMPLATE_ADMIN,  status="Admin Access", success=False)


#%% [5]
# ======================================================================================================    
# ======================================================================================================
# server start
# ======================================================================================================
# ======================================================================================================
HOST_IP =           args.host if args.host else '0.0.0.0'           # use "0.0.0.0" to listen on all interfaces
HOST_PORT =         args.port                                       # use 8080 by default
xprint(f'● server: {HOST_INFO} ~ {HOST_IP}:{HOST_PORT}')
octates = [ bool(int(x)) for x in HOST_IP.split('.') ]
display_HOST_IP = HOST_IP if True in octates else "localhost"
dprint(f'◉ running topics version: {__version__}')
dprint(f'◉ starting server @ {HOST_IP}:{HOST_PORT}')
#dprint(f'starting server @ {HOST_IP}:{HOST_PORT} \n\thttp://{display_HOST_IP}:{HOST_PORT}\n\thttp://{display_HOST_IP}:{HOST_PORT}/ref\n\thttp://{display_HOST_IP}:{HOST_PORT}/dbr\n\thttp://{display_HOST_IP}:{HOST_PORT}/dbw')
start_time = now()
print(f'visit http://{display_HOST_IP}:{HOST_PORT}')
serve(app, host=HOST_IP, port=HOST_PORT, max_request_body_size=MAX_UPLOAD_SIZE) 
# start serving app at this ip --> to stop app - use ctrl+c
stop_time = now()
dprint(f'◉ stopping server...')
while not write_db_to_disk(db):
    t = input('~ Press Enter to try again')
    if t: 
        dprint(f'! could not persist db to {LOGIN_XL_PATH}')
        break
dprint('◉ done! total up-time was {}'.format(stop_time-start_time))

# ======================================================================================================    
# ======================================================================================================
# server stop
# ======================================================================================================
# ======================================================================================================


# ======================================================================================================
# ADC data
# ======================================================================================================
if args.adc: 
    ADC_DIR = os.path.join(BASEDIR, args.adc)
    try: 
        os.makedirs(ADC_DIR, exist_ok=True)
        fid = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S%f")
        ADC_FILE = os.path.join(ADC_DIR, f'{fid}.json')
        import json
        o = dict(   
                    start_time=datetime.datetime.strftime(start_time, "%Y_%m_%d__%H_%M_%S__%f"),
                    stop_time=datetime.datetime.strftime(stop_time, "%Y_%m_%d__%H_%M_%S__%f"),
                    adc_login=adc_login, 
                    adc_downloads=adc_downloads, 
                    adc_uploads=adc_uploads, 
                    adc_purged=adc_purged,
        )
        with open(ADC_FILE, 'w') as f: json.dump(o, f, indent=4)
        xprint(f'⇒ Success writing ADC data at {ADC_DIR}/{ADC_FILE}')
    except:  xprint(f'⇒ Failed to write ADC data at {ADC_DIR}')
else: xprint(f'⇒ Skip writing ADC data')

print(f'◉ To report issues please visit [topics] at github: https://github.com/NelsonSharma/topics')
print(f'Finished!')
# ------------------------------------------------------------------------------------------
#%% [6]
# ------------------------------------------------------------------------------------------
# uncomment below to display adc on screen
# print(f"""
# ADC stats:
# ---------------------------------------
# Logins
# ---------------------------------------
# {adc_login}
# ---------------------------------------
# Downloads
# ---------------------------------------
# {adc_downloads}
# ---------------------------------------
# Uploads
# ---------------------------------------
# {adc_uploads}
# ---------------------------------------
# Purges
# ---------------------------------------
# {adc_purged}
# ---------------------------------------
# """)
""" FOOTNOTE 

"""

# ------------------------------------------------------------------------------------------