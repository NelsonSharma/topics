#-----------------------------------------------------------------------------------------
from sys import exit
if __name__!='__main__': exit(f'[!] can not import {__name__}.{__file__}')

__version__="2.4.1"
__doc__=f""" 
-------------------------------------------------------------
topics - Flask-based web app for sharing files 
-------------------------------------------------------------
Topics Version {__version__}
Page:   https://github.com/NelsonSharma/topics
Author: Nelson.S
-------------------------------------------------------------
Usage:
git clone https://github.com/NelsonSharma/topics.git
cd topics
python -m venv .venv
source .venv/bin/activate
python -m pip install Flask Flask-WTF waitress nbconvert
python -m pip install Flask==3.0.2 Flask-WTF==1.2.1 waitress==3.0.0 nbconvert==7.16.2
python topics.py 
-------------------------------------------------------------
Configs:
default `configs.py` file will be created
the dict named `current` will be choosen as the config
it should be defined at the end of the file
a config name `default` will be created 
it is used as a fall-back config
-------------------------------------------------------------
Note:
special string "::::" is used for replacing javascript on `repass` - uid and url should not contain this
special username 'None' is not allowed however words like 'none' will work
rename argument means (0 = not allowed) (1 = only rename) (2 = rename and remoji)
-------------------------------------------------------------


Note:
we use waitress for serving - which uses threads
threads in python are not really concurrent
all we need to do is declare variables as global when accessing from a thread
global variables are shared accross threads and not exclusive to thread
we must declare global variables only when writing to that variable but not on read 
"""

#%%
#-----------------------------------------------------------------------------------------
import os
OSENV = dict(os.environ)
def default_config_string(): return f"""
    'base' 		  :	"{OSENV.get('base', '__base__')}",
    'secret'	  :	"{OSENV.get('secret', '__secret__.txt')}",
    'login'       : "{OSENV.get('login', '__login__.csv')}",
    'rename'      : {int(OSENV.get('rename', 0))},
    'topic'       : "{OSENV.get('topic', 'tOpIcS')}",
    'emoji'       : "{OSENV.get('emoji', '💻')}",
    'welcome'     : "{OSENV.get('welcome', 'Welcome!')}",
    'case'        : {int(OSENV.get('case', 0))},
    'ext'         : "{OSENV.get('ext', '')}",
    'required'    : "{OSENV.get('required', '')}",
    'maxupcount'  : {int(OSENV.get('maxupcount', -1))},
    'maxupsize'   : "{OSENV.get('maxupsize', '1GB')}",
    'maxconnect'  : {int(OSENV.get('maxconnect', 100))},
    'port'        : "{OSENV.get('port', '8080')}",
    'host'        : "{OSENV.get('host', '0.0.0.0')}",
    'uploads'     : "{OSENV.get('uploads', '__uploads__')}",
    'downloads'   : "{OSENV.get('downloads', '__downloads__')}",
    'archives'    : "{OSENV.get('archives', '__archives__')}",
    'board'       : "{OSENV.get('board', '__board__.ipynb')}",
    'threads'     : {int(OSENV.get('threads', 4))},
    'verbose'     : {int(OSENV.get('verbose', 2))},
"""
def generate_default_config():
    return '\ndefault = {\n' + f'{default_config_string()}' + '\n}\n\ncurrent = default'
#-----------------------------------------------------------------------------------------
# check if 'configs.py` exsists or not`
PYDIR = os.path.dirname(__file__)
CONFIG = 'current'
CONFIG_MODULE = 'configs'
CONFIGS_FILE = f'{CONFIG_MODULE}.py'
CONFIGS_FILE_PATH = os.path.join(PYDIR, CONFIGS_FILE)
if not os.path.isfile(CONFIGS_FILE_PATH):
    print(f'↪ Creating default config "{CONFIGS_FILE}" from environment...')
    with open(CONFIGS_FILE_PATH, 'w', encoding='utf-8') as f: f.write(generate_default_config())

#-----------------------------------------------------------------------------------------

#%%

#-----------------------------------------------------------------------------------------
# Basic imports
#-----------------------------------------------------------------------------------------
import re, getpass, importlib
from math import inf
import datetime
fnow = datetime.datetime.strftime
dnow = datetime.datetime.now
now = lambda: fnow(dnow(),"%Y-%m-%d %H:%M:%S")

#-----------------------------------------------------------------------------------------
# Special Objects
#-----------------------------------------------------------------------------------------
class Fake:
    def __len__(self): return len(self.__dict__)
    def __init__(self, **kwargs) -> None:
        for name, attribute in kwargs.items():  setattr(self, name, attribute)

#-----------------------------------------------------------------------------------------
# Parse arguments
# ------------------------------------------------------------------------------------------
try: c_module = importlib.import_module(f'{CONFIG_MODULE}')
except: exit(f'[!] Could import configs module "{CONFIG_MODULE}"')
try:
    print(f'↪ Reading config from {CONFIG_MODULE}.{CONFIG}')
    config_dict = getattr(c_module, CONFIG)
    print(f'  ↦ type:{type(config_dict)}')
except:
    exit(f'[!] Could not read config from {CONFIG_MODULE}.{CONFIG}')

if not isinstance(config_dict, dict): 
    try: config_dict=config_dict()
    except: pass
if not isinstance(config_dict, dict): raise exit(f'Expecting a dict object for config')

try: 
    print(f'↪ Building config from {CONFIG_MODULE}.{CONFIG}')
    for k,v in config_dict.items():
        print(f'  ↦ {k}\t\t{v}')
    args = Fake(**config_dict)
except: exit(f'[!] config could not be loaded')
if not len(args): exit(f'[!] config was empty')
# for k in default_args: 
#     if not hasattr(args, k): exit(f'[!] config is missing attribute ({k})')
# ******************************************************************************************
        

#-----------------------------------------------------------------------------------------
# Create HTML
# ------------------------------------------------------------------------------------------
# ******************************************************************************************
HTML_TEMPLATES = dict(
board="""""",
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
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
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
        {% if '+' in session.admind %}
        <a href="{{ url_for('adminpage',req_cmd='dbw') }}" class="btn_admin">⚙ Persist login-db ↷</a>
        <br>
        <br>
        <a href="{{ url_for('adminpage',req_cmd='dbr') }}" class="btn_admin">⚙ Reload login-db ↺</a>
        <br>
        <br>
        <a href="{{ url_for('adminpage',req_cmd='upd') }}" class="btn_admin">⚙ Update download-list ▤</a>
        <br>
        <br>
        <a href="{{ url_for('adminpage',req_cmd='upa') }}" class="btn_admin">⚙ Update archive-list ⊞</a>
        <br>
        <br>
        <a href="{{ url_for('adminpage',req_cmd='ref') }}" class="btn_admin">⚙ Refresh board ▣</a>
        <br>
        <br>
        <button class="btn_admin" onclick="confirm_repass()">⚙ Reset Password ⨝</button>
            <script>
                function confirm_repass() {
                let res = prompt("Enter UID", ""); 
                if (res != null) {
                    location.href = "{{ url_for('repass',req_uid='::::') }}".replace("::::", res);
                    }
                }
            </script>
        <br>
        <br>
        {% endif %}
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
            {% if config.rename>0 %}
            <input id="named" name="named" type="text" placeholder="... update-name ..." class="txt_login"/>
            {% if config.rename>1 %}
            <input id="emojid" name="emojid" type="text" placeholder={{ config.emoji }} class="txt_login_small"/>
            {% endif %}
            <br>
            {% endif %}
            <br>
            <input type="submit" class="btn_login" value="Login"> 
            <br>
            <br>
        </form>
    </div>

    <!-- ---------------------------------------------------------->
    
    <div align="center">
    <div>
    <span style="font-size: xx-large;">{{ config.emoji }}</span>
    <br>
    
    </div>
    <!-- <a href="https://emojipicker.com/" target="_blank" class="btn_login">...</a> -->
    <!--<div style="font-size:large"><a href="https://github.com/NelsonSharma/topics"  target="_blank"> 📤 📥 </a></div>-->
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
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <a href="{{ url_for('logout') }}" class="btn_logout">Logout</a>
        <a href="{{ url_for('upload') }}" class="btn_download">Back</a>
        <a href="{{ url_for('download') }}" class="btn_refresh">Refresh</a>
        <br>
        <br>
        <div class="files_status">Downloads</div>
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
archive = """
<html>
    <head>
        <meta charset="UTF-8">
        <title> 🔶 {{ config.topic }} | {{ session.uid }} </title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">           
    </head>
    <body>
    <!-- ---------------------------------------------------------->
    </br>
    <!-- ---------------------------------------------------------->
    
    <div align="left" style="padding: 20px;">
        <div class="topic_mid">{{ config.topic }}</div>
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <a href="{{ url_for('logout') }}" class="btn_logout">Logout</a>
        <a href="{{ url_for('upload') }}" class="btn_download">Back</a>
        <a href="{{ url_for('archive') }}" class="btn_refresh">Refresh</a>
        <br>
        <br>
        <div class="files_status">Archives</div>
        <br>
        <div class="files_list_down">
            <ol>
            {% for file in config.afl %}
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
        <div class="userword">{{session.uid}} {{ session.emojid }} {{session.named}}</div>
        <br>
        <a href="{{ url_for('logout') }}" class="btn_logout">Logout</a>
        {% if "D" in session.admind %}
        <a href="{{ url_for('download') }}" class="btn_download">Downloads</a>
        {% endif %}
        {% if "A" in session.admind %}
        <a href="{{ url_for('archive') }}" class="btn_archive">Archives</a>
        {% endif %}
        {% if "U" in session.admind %}
        <a href="{{ url_for('uploadf') }}" class="btn_refresh">Refresh</a>
        {% endif %}
        {% if "B" in session.admind and config.board %}
        <a href="{{ url_for('board') }}" class="btn_board" target="_blank">Board</a>
        {% endif %}
        {% if '+' in session.admind %}
        <a href="{{ url_for('adminpage') }}" class="btn_admin">⚙</a>
        {% endif %}
        <br>
        <br>
        {% if config.muc!=0 and "U" in session.admind %}
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
        <div class="files_status">Uploads
        <button class="btn_purge" onclick="confirm_purge()">Purge</button>
            <script>
                function confirm_purge() {
                let res = confirm("Purge all the uploaded files now?");
                if (res == true) {
                    location.href = "{{ url_for('purge') }}";
                    }
                }
            </script>
        </div>
        <br>
        <div class="files_list_up">
            <ol>
            {% for f in session.filed %}
            <li>{{ f }}</li>
            {% endfor %}
            </ol>
        </div>
        <br>
        <br>
        {% endif %}
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


.txt_login_small{
    box-shadow: inset #abacaf 0 0 0 2px;
    text-align: center;
    font-family:monospace;
    border: 0;
    background: rgba(0, 0, 0, 0);
    appearance: none;
    position: absolute;
    border-radius: 3px;
    padding: 9px 12px;
    margin: 0px 0px 0px 4px;
    line-height: 1.4;
    color: rgb(0, 0, 0);
    font-size: 16px;
    font-weight: 400;
    height: 40px;
    width: 45px;
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
.btn_archive{
    padding: 2px 10px;
    background-color: #10a58a; 
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

.btn_board {
    padding: 2px 10px;
    background-color: #801abb; 
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
# ******************************************************************************************


#%%

# ------------------------------------------------------------------------------------------
# verbose levels
# dprints for user level logs
# sprint  for sever level logs
# ------------------------------------------------------------------------------------------

if args.verbose==0: # no log
    def sprint(msg): pass
    def dprint(msg): pass
elif args.verbose==1: # only server logs
    def sprint(msg): print(msg)
    def dprint(msg): pass 
elif args.verbose==2: # server and user logs
    def sprint(msg): print(msg)
    def dprint(msg): print(f'[{now()}]\t{msg}' )
else:
    def sprint(msg): pass
    def dprint(msg): pass
# ------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Rules
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
#HAS_PENDING = 0
CSV_DELIM=','
SSV_DELIM='\n'
MAX_STR_LEN=50
CSV_DTYPE=f'U{MAX_STR_LEN*2}'
# password policy
def VALIDATE_PASS(instr):   # a function that can validate the password - returns bool type
    try: assert (len(instr) < MAX_STR_LEN) and bool(re.fullmatch("(\w|@|\.)+", instr)) # alpha_numeric @.
    except AssertionError: return False
    return True
#-----------------------------------------------------------------------------------------
# uid policy
def VALIDATE_UID(instr):   # a function that can validate the uid - returns bool type
    try: assert (len(instr) < MAX_STR_LEN) and bool(re.fullmatch("(\w)+", instr)) # alpha_numeric 
    except AssertionError: return False
    return True
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
# name policy
def VALIDATE_NAME(instr): return  (len(instr) >0) and (len(instr) < MAX_STR_LEN) and bool(re.fullmatch("((\w)(\w|\s)*(\w))|(\w)", instr)) # alpha-neumeric but no illegal spaces before or after
#-----------------------------------------------------------------------------------------




# ------------------------------------------------------------------------------------------
# html pages
# ------------------------------------------------------------------------------------------
try:
    TEMPLATES_DIR, STATIC_DIR = os.path.join(PYDIR, "templates"), os.path.join(PYDIR, "static")
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    os.makedirs(STATIC_DIR, exist_ok=True)
    for k,v in HTML_TEMPLATES.items():
        with open(os.path.join(TEMPLATES_DIR, f"{k}.html"), 'w', encoding='utf-8') as f: f.write(v)
    for k,v in CSS_TEMPLATES.items():
        with open(os.path.join(STATIC_DIR, f"{k}.css"), 'w', encoding='utf-8') as f: f.write(v)
except: exit(f'[!] could not create html at {TEMPLATES_DIR} or {STATIC_DIR}')
# topics app 



#%% [1]
    
# Read base dir first 
BASEDIR = os.path.abspath((args.base if args.base else os.path.dirname(__file__)))
try:     os.makedirs(BASEDIR, exist_ok=True)
except:  exit(f'[!] base directory  @ {BASEDIR} was not found and could not be created') 
sprint(f'⚙ Base dicectiry:\t{BASEDIR}')
# ------------------------------------------------------------------------------------------
# WEB-SERVER INFORMATION
# ------------------------------------------------------------------------------------------\
if not args.secret: exit(f'[!] secret key was not provided!')
APP_SECRET_KEY_FILE = os.path.join(BASEDIR, args.secret)
if not os.path.isfile(APP_SECRET_KEY_FILE): #< --- if key dont exist, create it
    import random
    APP_SECRET_KEY = '{}:{}'.format(random.randint(1111111111, 9999999999), now())
    try:
        with open(APP_SECRET_KEY_FILE, 'w') as f: f.write(APP_SECRET_KEY) #<---- auto-generated key
    except: exit(f'[!] could not create secret key @ {APP_SECRET_KEY_FILE}')
    sprint(f'⇒ New secret created:\t{APP_SECRET_KEY_FILE}')
else:
    try:
        with open(APP_SECRET_KEY_FILE, 'r') as f: APP_SECRET_KEY = f.read()
        sprint(f'⇒ Loaded secret file:\t{APP_SECRET_KEY_FILE}')
    except: exit(f'[!] could not read secret key @ {APP_SECRET_KEY_FILE}')


# ------------------------------------------------------------------------------------------


#%% [2]
# ------------------------------------------------------------------------------------------
# LOGIN DATABASE - CSV
# ------------------------------------------------------------------------------------------
if not args.login: exit(f'[!] login file was not provided!')
LOGIN_XL_PATH = os.path.join( BASEDIR, args.login) 
LOGIN_ORD = ['ADMIN','UID','NAME','PASS']

def save_dict_to_csv(path, d):
    with open(path, 'w', encoding='utf-8') as f: 
        f.write(CSV_DELIM.join(LOGIN_ORD)+SSV_DELIM)
        for v in d.values(): f.write(CSV_DELIM.join(v)+SSV_DELIM)

def load_csv_to_dict(path):
    with open(path, 'r', encoding='utf-8') as f: 
        s = f.read()
        lines = s.split(SSV_DELIM)
        d = dict()
        for line in lines[1:]:
            if line:
                cells = line.split(CSV_DELIM)
                d[f'{cells[1]}'] = cells
        return d

if not os.path.isfile(LOGIN_XL_PATH): 
    sprint(f'⇒ Creating new login file:\t{LOGIN_XL_PATH}')
    this_user = getpass.getuser()
    sprint(f'⇒ Adding user {this_user} to login file:\t{LOGIN_XL_PATH}')
    if not (VALIDATE_UID(this_user)): 
        sprint(f'⇒⇒ Could create system user, creating default admin user')
        this_user='admin'
    save_dict_to_csv(LOGIN_XL_PATH, { f'{this_user}' : [f'DABU+',  f'{this_user}', f'{this_user}', f''] } ) # save updated login information to csv
    sprint(f'⇒ Created new login file:\t{LOGIN_XL_PATH}')
# ------------------------------------------------------------------------------------------

def read_db_from_disk():
    try:
        db_frame = load_csv_to_dict(LOGIN_XL_PATH)
        sprint(f'⇒ Loaded login file:\t{LOGIN_XL_PATH}')
    except:
        db_frame = dict()
        sprint(f'⇒ Failed reading login file:\t{LOGIN_XL_PATH}')
    
    return db_frame
# ------------------------------------------------------------------------------------------
def write_db_to_disk(db_frame): # will change the order
    try:
        save_dict_to_csv(LOGIN_XL_PATH, db_frame) # save updated login information to csv
        #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< PENDING DB
        sprint(f'⇒ Persisted login file:\t{LOGIN_XL_PATH}')
        return True
    except PermissionError:
        sprint(f'⇒ PermissionError - {LOGIN_XL_PATH} might be open, close it first.')
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
# download settings
# ------------------------------------------------------------------------------------------
if not args.downloads: exit(f'[!] downloads folder was not provided!')
DOWNLOAD_FOLDER_PATH = os.path.join( BASEDIR, args.downloads) 
try: os.makedirs(DOWNLOAD_FOLDER_PATH, exist_ok=True)
except: exit(f'[!] downloads folder @ {DOWNLOAD_FOLDER_PATH} was not found and could not be created')
sprint(f'⚙ Download Folder:\t{DOWNLOAD_FOLDER_PATH}')
def GET_DOWNLOAD_FILE_LIST (): 
    dlist = []
    d = DOWNLOAD_FOLDER_PATH
    for f in os.listdir(d):
        p = os.path.join(d, f)
        if os.path.isfile(p): dlist.append(f)
    return dlist
DOWNLOAD_FILE_LIST = GET_DOWNLOAD_FILE_LIST()
sprint(f'⚙ Download filelist\t{len(DOWNLOAD_FILE_LIST)} item(s)')
# ------------------------------------------------------------------------------------------
# archive settings
# ------------------------------------------------------------------------------------------
if not args.archives: exit(f'[!] archives folder was not provided!')
ARCHIVE_FOLDER_PATH = os.path.join( BASEDIR, args.archives) 
try: os.makedirs(ARCHIVE_FOLDER_PATH, exist_ok=True)
except: exit(f'[!] archives folder @ {ARCHIVE_FOLDER_PATH} was not found and could not be created')
sprint(f'⚙ Archive Folder:\t{ARCHIVE_FOLDER_PATH}')
def GET_ARCHIVE_FILE_LIST (): 
    dlist = []
    d = ARCHIVE_FOLDER_PATH
    for f in os.listdir(d):
        p = os.path.join(d, f)
        if os.path.isfile(p): dlist.append(f)
    return dlist
ARCHIVE_FILE_LIST = GET_ARCHIVE_FILE_LIST()
sprint(f'⚙ Archive filelist\t{len(ARCHIVE_FILE_LIST)} item(s)')


# ------------------------------------------------------------------------------------------
# upload settings
# ------------------------------------------------------------------------------------------
if not args.uploads: exit(f'[!] uploads folder was not provided!')
UPLOAD_FOLDER_PATH = os.path.join( BASEDIR, args.uploads ) 
try: os.makedirs(UPLOAD_FOLDER_PATH, exist_ok=True)
except: exit(f'[!] uploads folder @ {UPLOAD_FOLDER_PATH} was not found and could not be created')
sprint(f'⚙ Upload Folder:\t{UPLOAD_FOLDER_PATH}')




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


REQUIRED_FILES = set([x.strip() for x in args.required.split(',') if x])  # a set or list of file extensions that are allowed to be uploaded 
if '' in REQUIRED_FILES: REQUIRED_FILES.remove('')

def VALIDATE_FILENAME(filename):   # a function that checks for valid file extensions based on ALLOWED_EXTENSIONS
    if '.' in filename: 
        name, ext = filename.rsplit('.', 1)
        safename = f'{name}.{ext.lower()}'
        if REQUIRED_FILES:  isvalid = (safename in REQUIRED_FILES)
        else:               isvalid = bool(re.fullmatch(f'.+\.({VALID_FILES_PATTERN})$', safename))
    else:               
        name, ext = filename, ''
        safename = f'{name}'
        if REQUIRED_FILES:  isvalid = (safename in REQUIRED_FILES)
        else:               isvalid = (not ALLOWED_EXTENSIONS)
    return isvalid, safename

def str2bytes(size):
    sizes = dict(KB=2**10, MB=2**20, GB=2**30, TB=2**40)
    return int(float(size[:-2])*sizes.get(size[-2:].upper(), 0))
    
MAX_UPLOAD_SIZE = str2bytes(args.maxupsize)     # maximum upload file size 
MAX_UPLOAD_COUNT = ( inf if args.maxupcount<0 else args.maxupcount )       # maximum number of files that can be uploaded by one user
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
INITIAL_UPLOAD_STATUS.append((-1, f'max upload size:\t{mus_display}'))
if not (MAX_UPLOAD_COUNT is inf): INITIAL_UPLOAD_STATUS.append((-1, f'max upload count:\t{MAX_UPLOAD_COUNT}'))

sprint(f'⚙ Upload Settings ({len(INITIAL_UPLOAD_STATUS)})')
for s in INITIAL_UPLOAD_STATUS: sprint(f' ⇒ {s[1]}')
# ------------------------------------------------------------------------------------------
# download settings

# ------------------------------------------------------------------------------------------
#BOARD_FILE_HTML = os.path.join(TEMPLATES_DIR, f"board.html") #os.path.join(BASEDIR,  'templates', f'board.html')
BOARD_FILE_MD = None
try: 
    from nbconvert import HTMLExporter 
    if args.board:
        BOARD_FILE_MD = os.path.join(BASEDIR, f'{args.board}')
        if  os.path.isfile(BOARD_FILE_MD):
            sprint(f'⚙ Board File:\t{BOARD_FILE_MD}')
        else: 
            sprint(f'⚙ Board File:\t{BOARD_FILE_MD} not found - Board will not be available!')
            BOARD_FILE_MD = None
            # try: 
            #     with open(BOARD_FILE_MD, 'w', encoding='utf-8') as f: f.write(f"")
            # except: exit(f'[!] Board file {BOARD_FILE_MD} was not found and could not be created')

except:  BOARD_FILE_MD = None
if not BOARD_FILE_MD: sprint(f'⚙ Board File:\tNot Enabled')

def update_board(): 
    page=""
    if BOARD_FILE_MD:
        try: page,_ = HTMLExporter(template_name="classic").from_file(BOARD_FILE_MD, {'metadata':{'name':f'🔰 Board | {args.topic}'}}) 
        except: sprint(f'⚙ Board File could not be updated:\t{BOARD_FILE_MD}')
    return page
BOARD_PAGE=update_board()
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
app.config['archives'] =  ARCHIVE_FOLDER_PATH
app.config['emoji'] =     args.emoji
app.config['topic'] =     args.topic
app.config['dfl'] =       DOWNLOAD_FILE_LIST
app.config['afl'] =       ARCHIVE_FILE_LIST
app.config['rename'] =    int(args.rename)
app.config['muc'] =       MAX_UPLOAD_COUNT
app.config['board'] =     (BOARD_FILE_MD is not None)
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
    LOGIN_FAIL_TEXT =       '❌'              
    LOGIN_CREATE_TEXT =     '🔑'    
    #NAME, PASS = 2, 3
    global db#, HAS_PENDING#<--- only when writing to global wariables
    if request.method == 'POST' and 'uid' in request.form and 'passwd' in request.form:
        in_uid = f"{request.form['uid']}"
        in_passwd = f"{request.form['passwd']}"
        in_name = f'{request.form["named"]}' if 'named' in request.form else ''
        in_emoji = f'{request.form["emojid"]}' if 'emojid' in request.form else app.config['emoji']
        if ((not in_emoji) or (app.config['rename']<2)): in_emoji = app.config['emoji']
        in_query = in_uid if not args.case else (in_uid.upper() if args.case>0 else in_uid.lower())
        valid_query, valid_name = VALIDATE_UID(in_query) , VALIDATE_NAME(in_name)
        if not valid_query : record=None
        else: record = db.get(in_query, None) #print(f"◦ login attempt by [{in_uid}] will case-query [{in_query}]")
        #print(f"◦ record matched? [{record}]")
        if record is not None: 
            admind, uid, named, passwd = record
            admind = f'{admind}'.upper()
            #print(f"◦ matched record [{uid}|{named}] ")
            if not passwd: # fist login
                #print(f"◦ first login")
                if in_passwd: # new password provided
                    #print(f"[---------] new password provided [{in_passwd}]")
                    if VALIDATE_PASS(in_passwd): # new password is valid
                        db[uid][3]=in_passwd 
                        #HAS_PENDING+=1
                        if in_name!=named and valid_name and (app.config['rename']>0) : 
                            db[uid][2]=in_name
                            #HAS_PENDING+=1
                            dprint(f'⇒ {uid} ◦ {named} updated name to "{in_name}"') 
                            named = in_name
                        else:
                            if in_name: dprint(f'⇒ {uid} ◦ {named} provided invalid name "{in_name}" (will not update)') 
                        
                        #print(f'◦ updated record') # \n{record}

                        warn = LOGIN_CREATE_TEXT
                        msg = f'[{in_uid}] ({named}) New password was created successfully'
                        dprint(f'● {in_uid} {in_emoji} {named} just joined')
           
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
                            dprint(f'✗ directory could not be created @ {folder_name} :: Force logout user {uid}')
                            session['has_login'] = False
                            session['uid'] = uid
                            session['named'] = named
                            session['emojid'] = ''
                            return redirect(url_for('logout'))
                    
                        session['has_login'] = True
                        session['uid'] = uid
                        session['admind'] = admind
                        session['filed'] = os.listdir(folder_name)
                        session['emojid'] = in_emoji 
                        
                        if in_name!=named and  valid_name and  (app.config['rename']>0): 
                            session['named'] = in_name
                            db[uid][2] = in_name
                            #HAS_PENDING+=1
                            dprint(f'⇒ {uid} ◦ {named} updated name to "{in_name}"') 
                            named = in_name
                            #print(f'◦ updated record') # \n{record}
                        else: 
                            session['named'] = named
                            if in_name: dprint(f'⇒ {uid} ◦ {named} provided invalid name "{in_name}" (will not update)')  

                        #print(f'◦ login success {uid}|{named}')
                        dprint(f'● {session["uid"]} {session["emojid"]} {session["named"]} has logged in') 
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
        
    return render_template('login.html', msg = msg,  warn = warn)

@app.route('/logout')
def logout():
    r""" logout a user and redirect to login page """
    if not session.get('has_login', False):  return redirect(url_for('login'))
    if not session.get('uid', False): return redirect(url_for('login'))
    #print(f"◦ log out user {session['uid']}")
    if session['has_login']:  dprint(f'● {session["uid"]} {session["emojid"]} {session["named"]} has logged out') 
    else: dprint(f'✗ {session["uid"]} ◦ {session["named"]} was removed due to invalid uid ({session["uid"]})') 
    session['has_login'] = False
    session['uid'] = ""
    session['named'] = ""
    session['emojid'] = ""
    session['admind'] = ''
    session['filed'] = []
    return redirect(url_for('login'))
# ------------------------------------------------------------------------------------------



# ------------------------------------------------------------------------------------------
# board
# ------------------------------------------------------------------------------------------
@app.route('/board', methods =['GET'])
def board():
    if not session.get('has_login', False): return redirect(url_for('login'))
    if 'B' not in session['admind']:  return redirect(url_for('upload'))
    return BOARD_PAGE

# ------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------
# archive
# ------------------------------------------------------------------------------------------
@app.route('/archive', methods =['GET'], defaults={'req_path': ''})
@app.route('/archive/<path:req_path>')
def archive(req_path):
    if not session.get('has_login', False): return redirect(url_for('login'))
    if not 'A' in session['admind']: return redirect(url_for('upload'))
    abs_path = os.path.join(app.config['archives'], req_path) # Joining the base and the requested path
    #if req_path:print(f"◦ {session['uid']} trying to download {req_path}")
    if not os.path.exists(abs_path): 
        dprint(f"⇒ requested file was not found {abs_path}") #Return 404 if path doesn't exist
        return abort(404) 
    if os.path.isfile(abs_path):  #print(f"◦ sending file ")
        dprint(f'● {session["uid"]} ◦ {session["named"]} just downloaded the file {req_path}')
        return send_file(abs_path) # Check if path is a file and serve
    return render_template('archive.html')
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# download
# ------------------------------------------------------------------------------------------
@app.route('/download', methods =['GET'], defaults={'req_path': ''})
@app.route('/download/<path:req_path>')
def download(req_path):
    if not session.get('has_login', False): return redirect(url_for('login'))
    if 'D' not in session['admind']:  return redirect(url_for('upload'))
    abs_path = os.path.join(app.config['downloads'], req_path) # Joining the base and the requested path
    #if req_path:print(f"◦ {session['uid']} trying to download {req_path}")
    if not os.path.exists(abs_path): 
        dprint(f"⇒ requested file was not found {abs_path}") #Return 404 if path doesn't exist
        return abort(404) # print(f"◦ requested file was not found") #Return 404 if path doesn't exist
    if os.path.isfile(abs_path):  #print(f"◦ sending file ")
        dprint(f'● {session["uid"]} ◦ {session["named"]} just downloaded the file {req_path}')
        return send_file(abs_path) # Check if path is a file and serve
    return render_template('download.html')
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# upload
# ------------------------------------------------------------------------------------------
@app.route('/upload', methods =['GET', 'POST'])
def upload():
    if not session.get('has_login', False): return redirect(url_for('login'))
    #print( session['admind'])
    form = UploadFileForm()
    folder_name = os.path.join( app.config['uploads'], session['uid']) 
    #print(f"user {session['uid']} landed on upload page")    
    #print(f"..... has uploaded {len(file_list)} items")
    
    if form.validate_on_submit() and ('U' in session['admind']):
        dprint(f"⇒ user {session['uid']} ◦ {session['named']} is trying to upload {len(form.file.data)} items.")
        if app.config['muc']==0: 
            return render_template('upload.html', form=form, status=[(0, f'✗ Uploads are disabled')])
        else:
            result = []
            n_success = 0
            #---------------------------------------------------------------------------------
            for file in form.file.data:
                isvalid, sf = VALIDATE_FILENAME(secure_filename(file.filename))
                #print(f"[...........] {file.filename} {sf}")
            #---------------------------------------------------------------------------------
                
                if not isvalid:
                    why_failed =  f"✗ File not accepted [{sf}] " if REQUIRED_FILES else f"✗ Extension is invalid [{sf}] "
                    result.append((0, why_failed))
                    continue

                file_name = os.path.join(folder_name, sf)
                if not os.path.exists(file_name):
                    #file_list = os.listdir(folder_name)
                    if len(session['filed'])>=app.config['muc']:
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
            result_show = ''.join([f'\t{r[-1]}\n' for r in result])
            dprint(f'✓ {session["uid"]} ◦ {session["named"]} just uploaded {n_success} file(s)\n\n{result_show}') 
            return render_template('upload.html', form=form, status=result)
        
    #file_list = session['filed'] #os.listdir(folder_name)
    return render_template('upload.html', form=form, status=(INITIAL_UPLOAD_STATUS if app.config['muc']!=0 else [(-1, f'Uploads are disabled')]))
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
    if 'U' not in session['admind']:  return redirect(url_for('upload'))
    folder_name = os.path.join( app.config['uploads'], session['uid']) 
    if os.path.exists(folder_name):
        file_list = os.listdir(folder_name)
        for f in file_list: os.remove(os.path.join(folder_name, f))
        #print(f"◦ {session['uid']} has purged their files.")
        dprint(f'● {session["uid"]} ◦ {session["named"]} used purge')
        session['filed']=[]
        #dprint(f"filed @ purge= {session['filed']}")
    return redirect(url_for('upload'))
# ------------------------------------------------------------------------------------------

 
# ------------------------------------------------------------------------------------------
# administrative
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
@app.route('/admin/', methods =['GET'], defaults={'req_cmd': ''})
@app.route('/admin/<req_cmd>')
def adminpage(req_cmd):
    r""" opens admin page """ 
    if not session.get('has_login', False): return redirect(url_for('login')) # "Not Allowed - Requires Login"
    if '+' in session['admind']: 
        in_cmd = f'{req_cmd}'
        if in_cmd: 
            if   in_cmd=="upd": STATUS, SUCCESS = update_dl()
            elif in_cmd=="upa": STATUS, SUCCESS = update_al()
            elif in_cmd=="dbw": STATUS, SUCCESS = persist_db()
            elif in_cmd=="dbr": STATUS, SUCCESS = reload_db()
            elif in_cmd=="ref": STATUS, SUCCESS = refresh_board()
            else: STATUS, SUCCESS =  f"Invalid command '{in_cmd}'", False
        else: STATUS, SUCCESS =  f"Admin Access", True
    else: STATUS, SUCCESS =  "This action requires admin privilege", False
    return render_template('admin.html',  status=STATUS, success=SUCCESS)



def update_dl():
    r""" refreshes the  downloads"""
    app.config['dfl'] = GET_DOWNLOAD_FILE_LIST()
    dprint(f"▶ {session['uid']} ◦ {session['named']} just refreshed the download list.")
    return "Updated download-list", True #  STATUS, SUCCESS

def update_al():
    r""" refreshes the  downloads"""
    app.config['afl'] = GET_ARCHIVE_FILE_LIST()
    dprint(f"▶ {session['uid']} ◦ {session['named']} just refreshed the archive list.")
    return "Updated archive-list", True #  STATUS, SUCCESS


def persist_db():
    r""" writes db to disk """
    global db#,HAS_PENDING
    if write_db_to_disk(db):
        #HAS_PENDING=0
        dprint(f"▶ {session['uid']} ◦ {session['named']} just persisted the db to disk.")
        STATUS, SUCCESS = "Persisted db to disk", True
    else: STATUS, SUCCESS =  f"Write error '{args.login}' might be open", False
    return STATUS, SUCCESS 


def reload_db():
    r""" reloads db from disk """
    global db#, HAS_PENDING
    db = read_db_from_disk()
    #HAS_PENDING=0
    dprint(f"▶ {session['uid']} ◦ {session['named']} just reloaded the db from disk.")
    return "Reloaded db from disk", True #  STATUS, SUCCESS

def refresh_board():
    r""" refreshes the  board"""
    global BOARD_PAGE
    BOARD_PAGE=update_board()
    dprint(f"▶ {session['uid']} ◦ {session['named']} just refreshed the board.")
    return "Board was refreshed", True


# ------------------------------------------------------------------------------------------
# password reset
# ------------------------------------------------------------------------------------------
@app.route('/x/', methods =['GET'], defaults={'req_uid': ''})
@app.route('/x/<req_uid>')
def repass(req_uid):
    r""" reset user password"""
    if not session.get('has_login', False): return redirect(url_for('login')) # "Not Allowed - Requires Login"
    if '+' in session['admind']: 
        in_uid = f'{req_uid}'
        if in_uid: 
            in_query = in_uid if not args.case else (in_uid.upper() if args.case>0 else in_uid.lower())
            global db#, HAS_PENDING
            record = db.get(in_query, None)
            #print(f"◦ record matched? [{record is not None}]")
            if record is not None: 
                admind, uid, named, _ = record
                admind = f'{admind}'.upper()
                if '+' not in admind:
                    db[uid][3]='' ## 3 for PASS  record['PASS'].values[0]=''
                    #HAS_PENDING+=1
                    dprint(f"▶ {session['uid']} ◦ {session['named']} just reset the password for {uid} ◦ {named}")
                    STATUS, SUCCESS =  f"Password was reset for {uid} {named}", True
                else: STATUS, SUCCESS =  f"Cannot reset password for admin account '{in_query}'", False
            else: STATUS, SUCCESS =  f"User '{in_query}' not found - cannot reset password", False
        else: STATUS, SUCCESS =  f"Requires uid - use /x/<uid> to reset password", False
    else: STATUS, SUCCESS =  "This action requires admin privilege", False
    return render_template('admin.html',  status=STATUS, success=SUCCESS)
# ------------------------------------------------------------------------------------------













#%% @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#<-------------------DO NOT WRITE ANY CODE AFTER THIS
from waitress import serve
print('◉ start server @ [{}]'.format(datetime.datetime.now()))
endpoint = f'{args.host}:{args.port}' if args.host!='0.0.0.0' else f'localhost:{args.port}'
print(f'◉ http://{endpoint}')
serve(app, # https://docs.pylonsproject.org/projects/waitress/en/stable/runner.html
    host = args.host,          
    port = args.port,          
    url_scheme = 'http',     
    threads = args.threads,    
    connection_limit = args.maxconnect,
    max_request_body_size = MAX_UPLOAD_SIZE,
)
#<-------------------DO NOT WRITE ANY CODE AFTER THIS
