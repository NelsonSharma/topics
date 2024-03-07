#%%
__doc__=""" 
topics - Flask-based web app for sharing files 

git clone https://github.com/NelsonSharma/topics.git
cd topics

python -m venv .venv
source .venv/bin/activate

python -m pip install pandas openpyxl Flask Flask-WTF waitress
python -m pip install -r requirements.txt

python topics.py 

python topics.py --config=default

python topics.py --base="./__my base__" --secret="my secret.txt" --login="my login.xlsx" --rename=1 --topic="my topic" --emoji="🧡" --welcome="my greetings"  --case=0 --ext="txt,jpeg,jpeg,mp4,zip" --required="" --maxupcount=10 --maxupsize=256 --port=8080 --host=127.0.0.1 --uploads="my uploads" --downloads="my downloads" --threads=1 --verbose=3

https://github.com/NelsonSharma/topics
Author: Nelson.S
"""
__version__="2.3.25"
# ------------------------------------------------------------------------------------------
from sys import exit
if __name__!='__main__': exit(f'[!] can not import {__name__}.{__file__}')
class Fake:
    def __len__(self): return len(self.__dict__)
    def __init__(self, **kwargs) -> None:
        for name, attribute in kwargs.items():  setattr(self, name, attribute)
#%% configurations
class configs:
    r""" add your apps here """
    @staticmethod
    def default(): #<---- default configuration - do not delete - required to add arguments to argparser
        return {
        'base' 		  :	''				        ,
        'secret'	  :	'__secret__.txt'	    ,
        'login'       : '__login__.xlsx'	    ,
        'rename'      : 0					    ,
        'topic'       : 'tOpIcS'			    ,
        'emoji'       : '💻'				    ,
        'welcome'     : 'Welcome!'			    ,
        'case'        : 0					    ,
        'ext'         : ''					    ,
        'required'    : ''					    ,
        'maxupcount'  : 0					    ,
        'maxupsize'   : '1GB'					,
        'maxconnect'  : 100                     ,
        'port'        : '8080'				    ,
        'host'        : '0.0.0.0'			    ,
        'uploads'     : '__uploads__'		    ,
        'downloads'   : '__downloads__'		    ,
        'threads'     : 4			            ,
        'verbose'     : 0					    ,
        }

#%% basic imports
import os, re, platform
from math import inf
import datetime
now = datetime.datetime.now
HOST_INFO = f'{os.getlogin()}@{platform.node()}' 
#%% parse arguments
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
default_config = configs.default
default_args = default_config()
import argparse
parser = argparse.ArgumentParser()
parser.add_argument(f'--config', type=str, default='')
for k, v in default_args.items():parser.add_argument(f'--{k}', type=type(v), default=v)
args = parser.parse_args()
del parser

if args.config: # override everything
    try:
        c = f'{args.config}'
        if '.' in c:
            c_py, c_fun = c.split(".")
            import importlib
            c_module = importlib.import_module(c_py)
            if hasattr(c_module, c_fun): config_func_name = getattr(c_module, c_fun)
            else: raise NameError
        else:
            if hasattr(configs, c): config_func_name = getattr(configs, c)
            else: raise NameError
    except: 
        continue_default_config = input(f'↝ error loading config ({c}) press enter to use default')
        if f'{continue_default_config}': config_func_name = lambda:{}
        else: config_func_name = default_config
    finally: args = Fake(**(config_func_name()))

    if not len(args):exit(f'[!] config not provided')
    for k in default_args: 
        if not hasattr(args, k): exit(f'[!] config is missing attribute ({k})')
# ******************************************************************************************
HTML_TEMPLATES = dict(
# ******************************************************************************************
admin = """
<html>
	<head>
		<meta charset="UTF-8">
		<title> ⚙ {{ config.topic }} | {{ session.uid }} </title>
		<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">					 
	</head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ config['emoji'] }} {{session.named}}</div>
        <br>
        <a href="{{ url_for('logout') }}" class="btn_logout">Logout</a>
        <a href="{{ url_for('upload') }}" class="btn_download">Back</a>
        <a href="{{ url_for('adminpage') }}" class="btn_refresh">Refresh</a>
        <br>
        <br>

        {% if success %}
        <span class="admin_mid" style="animation-name: fader_admin_success;">✓ {{ status }} </span>
        {% else %}
        <span class="admin_mid" style="animation-name: fader_admin_failed;">✗ {{ status }} </span>
        {% endif %}
        <br>
        <br>
        <a href="{{ url_for('persist_db') }}" class="btn_admin">⚙ Persist login-db ↴</a>
        <br>
        <br>
        <a href="{{ url_for('reload_db') }}" class="btn_admin">⚙ Reload login-db ↺</a>
        <br>
        <br>
        <a href="{{ url_for('refresh_dll') }}" class="btn_admin">⚙ Update download-list ▤</a>
        <br>
        <br>

    </div>
			
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
# ******************************************************************************************
login = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> 🔒 {{ config.topic }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">  
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->

    <div align="center">
        <br>
        <div class="topic">{{ config.topic }}</div>
        <br>
        <br>
        <form action="{{ url_for('login') }}" method="post">
            <br>
            <div style="font-size: x-large;">{{ warn }}</div>
            <br>
            <div class="msg_login">{{ msg }}</div>
            <br>
            <input id="uid" name="uid" type="text" placeholder="... user-id ..." class="txt_login"/>
            <br>
            <br>
            <input id="passwd" name="passwd" type="password" placeholder="... password ..." class="txt_login"/>
            <br>
            <br>
            {% if config.rename %}
            <input id="named" name="named" type="text" placeholder="... update-name ..." class="txt_login"/>
            <br>
            <br>
            {% endif %}
            <input type="submit" class="btn_login" value="Login">
            <br>
            <br>

        </form>
    </div>
    <br>
    <br>
    <!-- ---------------------------------------------------------->
    
    <div align="center">
    <div><span style="font-size: xx-large;">{{ config.emoji }}</span><br><span class="info_login">{{ config.hostinfo }}</span></div>
    <div style="font-size:large">📤 <a href="https://github.com/NelsonSharma/topics" class="github_info"><i>topics</i> ● GitHub</a> 📥</div>
    <br>
    </div>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
# ******************************************************************************************
download = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> 🔻 {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">           
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ config['emoji'] }} {{session.named}}</div>
        <br>
        <a href="{{ url_for('logout') }}" class="btn_logout">Logout</a>
        <a href="{{ url_for('upload') }}" class="btn_download">Back</a>
        <a href="{{ url_for('download') }}" class="btn_refresh">Refresh</a>
        <br>
        <br>
        <div class="files_list_down">
            <ol>
            {% for file in config.dfl %}
            <li><a href="{{ (request.path + '/' if request.path != '/' else '') + file }}" style="text-decoration: none; color: rgb(20, 20, 20);" >{{ file }}</a></li>
            <br>
            {% endfor %}
            </ol>
        </div>
        <br>
        <br>
    </div>

    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
# ******************************************************************************************
upload="""
<html>
	<head>
		<meta charset="UTF-8">
		<title> 🔺 {{ config.topic }} | {{ session.uid }} </title>
		<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">					 
	</head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ config['emoji'] }} {{session.named}}</div>
        <br>
        <a href="{{ url_for('logout') }}" class="btn_logout">Logout</a>
        <a href="{{ url_for('download') }}" class="btn_download">Downloads</a>
        <a href="{{ url_for('uploadf') }}" class="btn_refresh">Refresh</a>
        <button class="btn_purge" onclick="confirm_purge()">Purge</button>
            <script>
                function confirm_purge() {
                let res = confirm("Purge all the uploaded files now?");
                if (res == true) {
                    location.href = "{{ url_for('purge') }}";
                    }
                }
            </script>
        {% if session.admind %}
        <a href="{{ url_for('adminpage') }}" class="btn_admin">⚙</a>
        {% endif %}
        <br>
        <br>
        <div class="status">
            <ol>
            {% for s,f in status %}
            {% if s %}
            {% if s<0 %}
            <li style="color: #ffffff;">{{ f }}</li>
            {% else %}
            <li style="color: #47ff6f;">{{ f }}</li>
            {% endif %}
            {% else %}
            <li style="color: #ff6565;">{{ f }}</li>
            {% endif %}
            {% endfor %}
            </ol>
        </div>
        <br>
        <form method='POST' enctype='multipart/form-data'>
            {{form.hidden_tag()}}
            {{form.file()}}
            {{form.submit()}}
        </form>
        <br>
        <div class="files_status">{{ msg }}</div>
        <br>
        <div class="files_list_up">
            <ol>
            {% for f in filelist %}
            <li>{{ f }}</li>
            {% endfor %}
            </ol>
        </div>
        <br>
        <br>

    </div>
			
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    </body>
</html>
""",
# ******************************************************************************************
)
CSS_TEMPLATES = dict(
# ******************************************************************************************
style = """
.github_info {
    padding: 2px 10px;
    background-color: #516fa7; 
    color: #ffffff;
    font-size: medium;
    font-weight: bold;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

  
.topic{
    color: #000000;
    font-size: xxx-large;
    font-weight: bold;
    font-family:monospace;    
}


.msg_login{
    color: #060472; 
    font-size: large;
    font-weight: bold;
    font-family:monospace;    
    animation-duration: 3s; 
    animation-name: fader_msg;
}
@keyframes fader_msg {from {color: #ffffff;} to {color: #060472; } }

.info_login{
    color: #3d3d3d; 
    font-size: large;
    font-weight: bold;
    font-family:monospace;    
}

.txt_login{

    text-align: center;
    font-family:monospace;

    box-shadow: inset #abacaf 0 0 0 2px;
    border: 0;
    background: rgba(0, 0, 0, 0);
    appearance: none;
    position: relative;
    border-radius: 3px;
    padding: 9px 12px;
    line-height: 1.4;
    color: rgb(0, 0, 0);
    font-size: 16px;
    font-weight: 400;
    height: 40px;
    transition: all .2s ease;
    :hover{
        box-shadow: 0 0 0 0 #fff inset, #1de9b6 0 0 0 2px;
    }
    :focus{
        background: #fff;
        outline: 0;
        box-shadow: 0 0 0 0 #fff inset, #1de9b6 0 0 0 3px;
    }
}
::placeholder {
    color: #888686;
    opacity: 1;
    font-weight: bold;
    font-style: oblique;
    font-family:monospace;   
}

.btn_login {
    padding: 2px 10px;
    background-color: #060472; 
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
    border-style:  none;
}

.topic_mid{
    color: #000000;
    font-size: x-large;
    font-style: italic;
    font-weight: bold;
    font-family:monospace;    
}



.btn_download {
    padding: 2px 10px;
    background-color: #089a28; 
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}
.userword{
    color: #12103c;
    font-weight: bold;
    font-family:monospace;    
    font-size: xxx-large;
}

.btn_logout {
    padding: 2px 10px;
    background-color: #060472; 
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}


.status{
    padding: 10px 10px;
    background-color: #232323; 
    color: #ffffff;
    font-size: medium;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}


.btn_refresh {
    padding: 2px 10px;
    background-color: #a19636; 
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.files_status{
    font-weight: bold;
    font-size: x-large;
    font-family:monospace;
}

.files_list_up{
    padding: 10px 10px;
    background-color: #ececec; 
    color: #080000;
    font-size: medium;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.files_list_down{
    padding: 10px 10px;
    background-color: #ececec; 
    color: #080000;
    font-size: x-large;
    font-weight: bold;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}


.btn_purge {
    padding: 2px 10px;
    background-color: #9a0808; 
    border-style: none;
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}

.btn_admin {
    padding: 2px 10px;
    background-color: #000000; 
    border-style: none;
    color: #FFFFFF;
    font-weight: bold;
    font-size: large;
    border-radius: 10px;
    font-family:monospace;
    text-decoration: none;
}


.admin_mid{
    color: #000000; 
    font-size: x-large;
    font-weight: bold;
    font-family:monospace;    
    animation-duration: 10s;
}
@keyframes fader_admin_failed {from {color: #ff0000;} to {color: #000000; } }
@keyframes fader_admin_success {from {color: #22ff00;} to {color: #000000; } }
"""
)
#%%
# ------------------------------------------------------------------------------------------
# html pages
# ------------------------------------------------------------------------------------------
try:
    PYDIR = os.path.dirname(__file__)
    TEMPLATES_DIR, STATIC_DIR = os.path.join(PYDIR, "templates"), os.path.join(PYDIR, "static")
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)
    for k,v in HTML_TEMPLATES.items():
        with open(os.path.join(TEMPLATES_DIR, f"{k}.html"), 'w', encoding='utf-8') as f: f.write(v)
    for k,v in CSS_TEMPLATES.items():
        with open(os.path.join(STATIC_DIR, f"{k}.css"), 'w', encoding='utf-8') as f: f.write(v)
except: exit(f'[!] could not create html at {TEMPLATES_DIR} or {STATIC_DIR}')
# topics app 

# ------------------------------------------------------------------------------------------
# verbose levels
# ------------------------------------------------------------------------------------------
if args.verbose==0:
    def dprint(msg): pass
elif args.verbose==1:
    def dprint(msg): print(msg)
elif args.verbose==2:
    def dprint(msg): print(f'[{now()}]\t{msg}' )
else:
    def dprint(msg): pass
# ------------------------------------------------------------------------------------------


#%% [1]
    
# Read base dir first 

BASEDIR = os.path.abspath((args.base if args.base else os.path.dirname(__file__)))
try:     os.makedirs(BASEDIR, exist_ok=True)
except:  exit(f'[!] base directory  @ {BASEDIR} was not found and could not be created') 
dprint(f'⚙ Base dicectiry:\t{BASEDIR}')
# ------------------------------------------------------------------------------------------
# WEB-SERVER INFORMATION
# ------------------------------------------------------------------------------------------\
if not args.secret: exit(f'[!] secret key was not provided!')
APP_SECRET_KEY_FILE = os.path.join(BASEDIR, args.secret)
if not os.path.isfile(APP_SECRET_KEY_FILE): #< --- if key dont exist, create it
    APP_SECRET_KEY = '{}:{}'.format(HOST_INFO, now())
    try:
        with open(APP_SECRET_KEY_FILE, 'w') as f: f.write(APP_SECRET_KEY) #<---- auto-generated key
    except: exit(f'[!] could not create secret key @ {APP_SECRET_KEY_FILE}')
    dprint(f'⇒ New secret created:\t{APP_SECRET_KEY_FILE}')
else:
    try:
        with open(APP_SECRET_KEY_FILE, 'r') as f: APP_SECRET_KEY = f.read()
        dprint(f'⇒ Load secret from:\t{APP_SECRET_KEY_FILE}')
    except: exit(f'[!] could not read secret key @ {APP_SECRET_KEY_FILE}')


# ------------------------------------------------------------------------------------------


#%% [2]
from pandas import DataFrame, read_excel, isnull
# ------------------------------------------------------------------------------------------
# LOGIN DATABASE - EXCEL
# ------------------------------------------------------------------------------------------
if not args.login: exit(f'[!] login file was not provided!')
LOGIN_XL_PATH = os.path.join( BASEDIR, args.login) 
if not os.path.isfile(LOGIN_XL_PATH): 
    #print(f'⇒ Login file {LOGIN_XL_PATH} not found - creating new...')
    db_dict = { #<---------------- default login file
        'ADMIN': [f'+'], #<---- any non blank string will work
        'UID': [f'{os.getlogin()}'],
        'NAME': [f'{platform.node()}'],
        'PASS': [''],
        }
    db_frame = DataFrame( db_dict )
    for si in ['ADMIN', 'UID', 'NAME', 'PASS']: db_frame[si] = db_frame[si].astype(object)
    #print(f'Created New db\n{db_frame}\n')
    db_frame.to_excel(LOGIN_XL_PATH, sheet_name="login", index=False) # save updated login information to excel sheet
    del db_dict, db_frame
    dprint(f'⇒ Created new login file:\t{LOGIN_XL_PATH}')
# ------------------------------------------------------------------------------------------
def read_db_from_disk():
    db_frame = read_excel(LOGIN_XL_PATH, dtype=str, engine='openpyxl') #<---- reading an invalid excel file may throw error - to be handled by user
    for si in ['ADMIN', 'UID', 'NAME', 'PASS']: db_frame[si] = db_frame[si].astype(object)
    #print(f'Loaded db\n{db_frame}\n')
    dprint(f'⇒ Loaded login file:\t{LOGIN_XL_PATH}')
    return db_frame
# ------------------------------------------------------------------------------------------
def write_db_to_disk(db_frame): 
    try:
        db_frame.to_excel(LOGIN_XL_PATH, engine='openpyxl', sheet_name="login", index=False) # save updated login information to excel sheet
        #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< PENDING DB
        dprint(f'⇒ Persisted login file:\t{LOGIN_XL_PATH}')
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
if not args.downloads: exit(f'[!] downloads folder was not provided!')
DOWNLOAD_FOLDER_PATH = os.path.join( BASEDIR, args.downloads) 
try: os.makedirs(DOWNLOAD_FOLDER_PATH, exist_ok=True)
except: exit(f'[!] downloads folder @ {DOWNLOAD_FOLDER_PATH} was not found and count not be created')
dprint(f'⚙ Download Folder:\t{DOWNLOAD_FOLDER_PATH}')
def GET_DOWNLOAD_FILE_LIST (): 
    dlist = []
    d = DOWNLOAD_FOLDER_PATH
    for f in os.listdir(d):
        p = os.path.join(d, f)
        if os.path.isfile(p): dlist.append(f)
    return dlist
DOWNLOAD_FILE_LIST = GET_DOWNLOAD_FILE_LIST()
dprint(f'⚙ Download filelist\t{len(DOWNLOAD_FILE_LIST)} item(s)')

# ------------------------------------------------------------------------------------------
# upload settings
# ------------------------------------------------------------------------------------------
if not args.uploads: exit(f'[!] uploads folder was not provided!')
UPLOAD_FOLDER_PATH = os.path.join( BASEDIR, args.uploads ) 
try: os.makedirs(UPLOAD_FOLDER_PATH, exist_ok=True)
except: exit(f'[!] uploads folder @ {UPLOAD_FOLDER_PATH} was not found and count not be created')
dprint(f'⚙ Upload Folder:\t{UPLOAD_FOLDER_PATH}')




# ------------------------------------------------------------------------------------------
# validation
# ------------------------------------------------------------------------------------------

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

def str2bytes(size):
    sizes = dict(KB=2**10, MB=2**20, GB=2**30, TB=2**40)
    return int(float(size[:-2])*sizes.get(size[-2:].upper(), 0))
    
MAX_UPLOAD_SIZE = str2bytes(args.maxupsize)     # maximum upload file size 
MAX_UPLOAD_COUNT = abs(args.maxupcount) if args.maxupcount else inf        # maximum number of files that can be uploaded by one user
# find max upload size in appropiate units
mus_kb = MAX_UPLOAD_SIZE/(2**10)
if len(f'{int(mus_kb)}') < 4:
    mus_display = f'{mus_kb:.2f} KB'
else:
    mus_mb = MAX_UPLOAD_SIZE/(2**20)
    if len(f'{int(mus_mb)}') < 4:
        mus_display = f'{mus_mb:.2f} MB'
    else:
        mus_gb = MAX_UPLOAD_SIZE/(2**30)
        if len(f'{int(mus_gb)}') < 4:
            mus_display = f'{mus_gb:.2f} GB'
        else:
            mus_tb = MAX_UPLOAD_SIZE/(2**40)
            mus_display = f'{mus_tb:.2f} TB'

INITIAL_UPLOAD_STATUS = []           # a list of notes to be displayed to the users about uploading files
if REQUIRED_FILES:
    INITIAL_UPLOAD_STATUS.append((-1, f'accepted files [{len(REQUIRED_FILES)}]:\t{REQUIRED_FILES}'))
else:
    if ALLOWED_EXTENSIONS:  INITIAL_UPLOAD_STATUS.append((-1, f'allowed extensions [{len(ALLOWED_EXTENSIONS)}]:\t{ALLOWED_EXTENSIONS}'))
    #else:                   INITIAL_UPLOAD_STATUS.append((-1, f'allowed extensions:\tany'))
INITIAL_UPLOAD_STATUS.append((-1, f'max file-size:\t{mus_display}'))
if not (MAX_UPLOAD_COUNT is inf): INITIAL_UPLOAD_STATUS.append((-1, f'max file-count:\t{MAX_UPLOAD_COUNT}'))

dprint(f'⚙ Upload Settings:\n{INITIAL_UPLOAD_STATUS}')
# ------------------------------------------------------------------------------------------
# download settings
# ------------------------------------------------------------------------------------------



# ------------------------------------------------------------------------------------------
# imports ----------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
from flask import Flask, render_template, request, redirect, url_for, session, abort, send_file
from flask_wtf import FlaskForm
from wtforms import SubmitField, MultipleFileField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
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
class UploadFileForm(FlaskForm): # The upload form using FlaskForm
    file = MultipleFileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")
# HTML templates




# ------------------------------------------------------------------------------------------


#%% [4]
# app.route  > all app.route implemented here 
# ------------------------------------------------------------------------------------------
# login
# ------------------------------------------------------------------------------------------
@app.route('/', methods =['GET', 'POST'])
def login():
    LOGIN_NEED_TEXT =       '🔒'
    LOGIN_FAIL_TEXT =       '🔥'              
    LOGIN_CREATE_TEXT =     '🔑'    
    TEMPLATE_LOGIN =    'login.html'
    global db
    if request.method == 'POST' and 'uid' in request.form and 'passwd' in request.form:
        in_uid = f"{request.form['uid']}"
        in_passwd = f"{request.form['passwd']}"
        in_name = f'{request.form["named"]}' if 'named' in request.form else ''
        in_query = in_uid if not args.case else (in_uid.upper() if args.case>0 else in_uid.lower())
        #print(f"◦ login attempt by [{in_uid}] will case-query [{in_query}]")

        try:                record = db.query("UID==@in_query")
        except KeyError:    record = None
        if not len(record): record=None
        #print(f"◦ record matched? [{record is not None}]")
        if record is not None: 
            passwd = record['PASS'].values[0]
            named = record['NAME'].values[0]
            uid = record['UID'].values[0]
            admind = record['ADMIN'].values[0]
            if isnull(admind): admind=''
            #print(f'{passwd=}, {named=}, {uid=}, {admind=}')
            #print(f"◦ matched record [{uid}|{named}]")
            if isnull(passwd) or passwd=='': # fist login
                #print(f"◦ first login")
                if in_passwd: # new password provided
                    #print(f"[---------] new password provided [{in_passwd}]")
                    if VALIDATE_PASSWORD(in_passwd): # new password is valid
                        #print(f"[---------] new password is valid")  
                        record['PASS'].values[0]=in_passwd 
                        if in_name and in_name!=named and app.config['rename'] : 
                            record['NAME'].values[0]=in_name
                            named = in_name
                        db.update(record) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< PENDING DB
                        #print(f'◦ updated record') # \n{record}

                        warn = LOGIN_CREATE_TEXT
                        msg = f'[{in_uid}.{named}] New password was created successfully'
                        dprint(f'● {in_uid}.{named} just joined')
           
                    else: # new password is invalid valid
                        #print(f"[........] new password is invalid")  
                        warn = LOGIN_FAIL_TEXT
                        msg=f'[{in_uid}] New password is invalid - can use alpha-numeric, underscore and @-symbol'
                        
                                               
                else: #new password not provided       
                    #print(f"[.....] new password was not provided")             
                    warn = LOGIN_FAIL_TEXT
                    msg = f'[{in_uid}] New password required - can use alpha-numeric, underscore and @-symbol'
                                           
            else: # re login
                #print(f"◦ revist login")
                if in_passwd: # password provided
                    #print(f"[........] password provided {in_passwd}")  
                    if in_passwd==passwd:
                        #print(f"[......] password does match") 
                        folder_name = os.path.join(app.config['uploads'], uid) 
                        #print(f"user {session['uid']} landed on upload page")
                        try:
                            os.makedirs(folder_name, exist_ok=True)
                            #print(f"..... has directory {folder_name}")
                        except:
                            dprint(f'◦ directory could not be created @ {folder_name} :: Force logout user {uid}')
                            session['has_login'] = False
                            session['uid'] = uid
                            session['named'] = named
                            return redirect(url_for('logout'))
                    
                        session['has_login'] = True
                        session['uid'] = uid
                        session['admind'] = admind
                        session['filed'] = os.listdir(folder_name)
                        
                        if in_name and in_name!=named and app.config['rename']: 
                            session['named'] = in_name
                            record['NAME'].values[0]=in_name
                            db.update(record) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< PENDING DB
                            named = in_name
                            #print(f'◦ updated record') # \n{record}
                        else: session['named'] = named

                        #print(f'◦ login success {uid}|{named}')
                        dprint(f'● {session["uid"]}.{session["named"]} has logged in') 
                        #print(f"filed @ login= {session['filed']}")
                        return redirect(url_for('upload'))
                    else:  
                        #print(f"[.....] password does not match")  
                        warn = LOGIN_FAIL_TEXT
                        msg = f'[{in_uid}] Password mismatch'                  
                else: # password not provided
                    #print(f"[....] password not provided")  
                    warn = LOGIN_FAIL_TEXT
                    msg = f'[{in_uid}] Password not provided'
        else:
            #print(f"◦ unmatched record {in_uid}")
            warn = LOGIN_FAIL_TEXT
            msg = f'[{in_uid}] Not a valid user'                      
    else:
        if session.get('has_login', False):  return redirect(url_for('upload'))
        #print(f"+ page hit")
        msg = args.welcome
        warn = LOGIN_NEED_TEXT 
        
    return render_template(TEMPLATE_LOGIN, msg = msg,  warn = warn)

@app.route('/logout')
def logout():
    r""" logout a user and redirect to login page """
    if not session.get('has_login', False):  return redirect(url_for('login'))
    if not session.get('uid', False): return redirect(url_for('login'))
    #print(f"◦ log out user {session['uid']}")
    if session['has_login']:  dprint(f'● {session["uid"]}.{session["named"]} has logged out') 
    else: dprint(f'● {session["uid"]}.{session["named"]} was removed due to invalid uid ({session["uid"]})') 
    session['has_login'] = False
    session['uid'] = ""
    session['named'] = ""
    session['admind'] = ""
    session['filed'] = []
    return redirect(url_for('login'))
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# download
# ------------------------------------------------------------------------------------------
@app.route('/download', methods =['GET'], defaults={'req_path': ''})
@app.route('/download/<path:req_path>')
def download(req_path):
    TEMPLATE_DOWNLOAD = 'download.html'
    if not session.get('has_login', False): return redirect(url_for('login'))
    abs_path = os.path.join(app.config['downloads'], req_path) # Joining the base and the requested path
    #if req_path:print(f"◦ {session['uid']} trying to download {req_path}")
    if not os.path.exists(abs_path): return abort(404) # print(f"◦ requested file was not found") #Return 404 if path doesn't exist
    if os.path.isfile(abs_path):  #print(f"◦ sending file ")
        dprint(f'● {session["uid"]}.{session["named"]} just downloaded the file {req_path}')
        return send_file(abs_path) # Check if path is a file and serve
    return render_template(TEMPLATE_DOWNLOAD)
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# upload
# ------------------------------------------------------------------------------------------
@app.route('/upload', methods =['GET', 'POST'])
def upload():
    TEMPLATE_UPLOAD =   'upload.html'
    if not session.get('has_login', False): return redirect(url_for('login'))
    form = UploadFileForm()
    folder_name = os.path.join( app.config['uploads'], session['uid']) 
    #print(f"user {session['uid']} landed on upload page")    
    #print(f"..... has uploaded {len(file_list)} items")

    if form.validate_on_submit():
        dprint(f"◦ user {session['uid']} is trying to upload {len(form.file.data)} items.")
        result = []
        n_success = 0
        #---------------------------------------------------------------------------------
        for file in form.file.data:
            sf = secure_filename(file.filename)
            #print(f"[...........] {file.filename} {sf}")
        #---------------------------------------------------------------------------------
            if not VALIDATE_FILENAME(sf):
                why_failed =  f"✗ File not accepted [{sf}] " if REQUIRED_FILES else f"✗ Extension is invalid [{sf}] "
                result.append((0, why_failed))
                continue

            file_name = os.path.join(folder_name, sf)
            if not os.path.exists(file_name):
                #file_list = os.listdir(folder_name)
                if len(session['filed'])>=MAX_UPLOAD_COUNT:
                    why_failed = f"✗ Upload limit reached [{sf}] "
                    result.append((0, why_failed))
                    continue

            file.save(file_name) 
            why_failed = f"✓ Uploaded new file [{sf}] "
            result.append((1, why_failed))
            n_success+=1
            if sf not in session['filed']: session['filed'] = session['filed'] + [sf]

        #---------------------------------------------------------------------------------
        
        #print(f"◦ upload results: \n{result}")
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
        #print(f"◦ {session['uid']} has purged their files.")
        dprint(f'● {session["uid"]}.{session["named"]} used purge')
        session['filed']=[]
        #dprint(f"filed @ purge= {session['filed']}")
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



#%% @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def SERVE(webapp, host, port, url, threads, max_connect, max_body, **kwargs):
    import datetime
    from waitress import serve
    start_time = datetime.datetime.now()
    print('◉ start server @ {}'.format(start_time))
    endpoint = f'{host}:{port}' if host!='0.0.0.0' else f'localhost:{port}'
    print(f'▶ {url.lower()}://{endpoint}')
    serve(webapp, # https://docs.pylonsproject.org/projects/waitress/en/stable/runner.html
        host = host,          
        port = port,          
        url_scheme = url,     
        threads = threads,    
        connection_limit = max_connect,
        max_request_body_size = max_body,
        **kwargs)
    stop_time = datetime.datetime.now()
    run_time = stop_time-start_time
    print('◉ stop server @ {}'.format(stop_time))
    print('◉ total up-time was {}'.format(run_time))
    return

#%% @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
print(f'Starting...')
#%% @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
SERVE(
    webapp=     app,
    host=       args.host, 
    port=       args.port, 
    url=        'http', 
    threads=    args.threads, 
    max_connect=args.maxconnect, 
    max_body=   MAX_UPLOAD_SIZE, 
)
#%%
while not write_db_to_disk(db):
    t = input('↝ Persist error ~ Press Enter to try again')
    if t: 
        print(f'⇒ could not persist db to {LOGIN_XL_PATH}')
        break
try:
    for k,v in HTML_TEMPLATES.items(): os.remove(os.path.join(TEMPLATES_DIR, f"{k}.html"))
    for k,v in CSS_TEMPLATES.items(): os.remove(os.path.join(STATIC_DIR, f"{k}.css"))
    os.removedirs(TEMPLATES_DIR), os.removedirs(STATIC_DIR)
except: print(f'⇒ could not remove html at {TEMPLATES_DIR} or {STATIC_DIR}')
#%% @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
print(f'Finished!')
