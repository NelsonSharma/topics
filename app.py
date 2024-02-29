
__doc__=""" Topics - Flask based web app for sharing files """




if __name__!='__main__':
    print(f'cannot import this file')
    from sys import exit
    exit()


# parse arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--topic',          type=str,       default='tOpIcS',          help='the main topic/subject')
parser.add_argument('--login',          type=str,       default='__login__.xlsx',      help='login excel file')
parser.add_argument('--case',           type=int,       default=0,                 help='convert login roll to upper or lower case (-1 means lower-case, 1 means upper-case) (0 means as it is) ')
parser.add_argument('--ext',            type=str,       default='',                help='csv string of allowed file extensions, keep blank to allow all')
parser.add_argument('--maxupfiles',     type=int,       default=500,               help='maximum number of files that can be uploaded')
parser.add_argument('--maxupsize',      type=float,     default=10240.0,           help='maximum size (in MB) of file that can be uploaded')

parser.add_argument('--port',           type=int,       default=8080,              help='port to host web server')
parser.add_argument('--host',           type=str,       default='',                help='ip-address to host web server, leave blank to server on all IPs - same as 0.0.0.0')

parser.add_argument('--uploads',        type=str,       default='__uploads__',         help='uploads folder')
parser.add_argument('--downloads',      type=str,       default='__downloads__',       help='downloads folder')

parser.add_argument('--default',        type=int,       default=1,                 help='if 0 then no user will be created when the supplied login file is not present')

args = parser.parse_args()

# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------

# imports ----------------------------------------------------------------------------------
import platform, re, os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, abort, send_file
from flask_wtf import FlaskForm
from wtforms import SubmitField, MultipleFileField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
from waitress import serve
# ------------------------------------------------------------------------------------------
HOST_ALIAS = f'{os.getlogin()} @ {platform.node()}:{platform.system()}.{platform.release()}'
APP_SECRET_KEY = HOST_ALIAS
# ------------------------------------------------------------------------------------------

""" WEB-SERVER HOST INFORMATION """
HOST_IP =       args.host if args.host else '0.0.0.0'        # use "0.0.0.0" to listen on all interfaces
HOST_PORT =     args.port         # use 80 by default
# ------------------------------------------------------------------------------------------

"""SECTION [A]: reading login information 
    > read login info from an excel (.xlsx) file using pd.read_excel
    > `LOGIN_XL` contain excel file-name 
    > the sheet should have 3 cols -> [ ROLL  NAME  PASS ]
    
    > the `ROLL` field is the unique-id usually the roll number - used to login
    > only those roll numbers that are populated in the `ROLL` field will be allowed to login and use app
    > one should pre-fill the `ROLL` fields with student list

    > the `NAME` field represents the students full name - should be prefiled along with `ROLL`

    > the `PASS` field is the password for login
    > its initially kept blank - keeping it blank allows for the user to set password
    > this simulates the first-time login

    > NOTE - 
        ~> at least one record must be entered so that when pandas reads this excel it knows what data-type is expected in each col
        ~> add a dummy record in the login sheet to hint at data-types
            specially with the `PASS` coloumn
            otherwise pandas will interpret `PASS` coloumn as float data-type
"""
LOGIN_XL = args.login   # excel file that contains login information
LOGIN_XL_PATH = os.path.join( os.path.abspath(os.path.dirname(__file__)), LOGIN_XL) 
if not os.path.isfile(LOGIN_XL_PATH): 
    print(f'Login file {LOGIN_XL} @ {LOGIN_XL_PATH} not found - creating new...')
    DEFAULT_ROLL = args.default
    db_dict = { #<---------------- default login file
        'ROLL': [f'{os.getlogin()}'] if DEFAULT_ROLL else [],
        'NAME': [f'{platform.node()}'] if DEFAULT_ROLL else [],
        'PASS': [''] if DEFAULT_ROLL else [],
        }
    print(f'{DEFAULT_ROLL=}\n{db_dict=}')
    db = pd.DataFrame( db_dict )
    for si in ['ROLL', 'NAME', 'PASS']: db[si] = db[si].astype(object)
    
    db.to_excel(LOGIN_XL_PATH, sheet_name="login", index=False) # save updated login information to excel sheet
    del db_dict, db
    print(f'Created new login file {LOGIN_XL} @ {LOGIN_XL_PATH}')
    

db = pd.read_excel(LOGIN_XL_PATH) #<---- reading an invalid excel file may throw error - to be handled by user
for si in ['ROLL', 'NAME', 'PASS']: db[si] = db[si].astype(object)
# ------------------------------------------------------------------------------------------

"""SECTION [B]: Meta information
    > set some meta-information about the production scenario
"""
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
INVALID_PASSWORD_WARN = f'Password should be atleast {MIN_PASSWORD_LEN} char(s) - can use alpha-numeric and underscore only' # a warning msg to be displayed when incorrect password is created
def VALIDATE_PASSWORD(password):   # a function that can validate the password - returns bool type
    try:
        assert len(password) >= MIN_PASSWORD_LEN
        assert len(re.findall("[a-zA-Z]|[0-9]|_", password)) == len(password)
        return True
    except AssertionError: return False

# ------------------------------------------------------------------------------------------
# upload settings
# ------------------------------------------------------------------------------------------
UPLOAD_FOLDER = args.uploads           # this is with respect to current script (__file__) - files are uploaded under each users folder
UPLOAD_FOLDER_PATH = os.path.join( os.path.abspath(os.path.dirname(__file__)), UPLOAD_FOLDER) 
os.makedirs(UPLOAD_FOLDER_PATH, exist_ok=True)
ALLOWED_EXTENSIONS = set([]) if not args.ext else set(args.ext.split(','))  # a set or list of file extensions that are allowed to be uploaded e.g - {'txt', 'py', 'zip', 'jpg', 'mp4'}
def VALIDATE_EXTENSION(filename):   # a function that checks for valid file extensions based on ALLOWED_EXTENSIONS
    if len(ALLOWED_EXTENSIONS): return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    else: return True
MB = 2**20                                        # 1 MB in bytes
MAX_UPLOAD_SIZE = int(abs(args.maxupsize*MB))         # maximum upload file size 
MAX_UPLOAD_COUNT = int(abs(args.maxupfiles))               # maximum number of files that can be uploaded by one user/roll
INITIAL_UPLOAD_STATUS = [           # a list of notes to be displayed to the users about uploading files
    f'upload files here - existing files will be overwritten',
    f'allowed extensions are {ALLOWED_EXTENSIONS}',
    f'maximum allowed file SIZE is {int(abs(args.maxupsize)):.2f} MB',
    f'maximum allowed file COUNT is {MAX_UPLOAD_COUNT} files',
]

# ------------------------------------------------------------------------------------------
# download settings
# ------------------------------------------------------------------------------------------
DOWNLOAD_FOLDER = args.downloads       # this is with respect to current script (__file__) - represents the "resources" page
DOWNLOAD_FOLDER_PATH = os.path.join( os.path.abspath(os.path.dirname(__file__)), DOWNLOAD_FOLDER) 
os.makedirs(DOWNLOAD_FOLDER_PATH, exist_ok=True)
# DOWNLOAD_FILE_LIST is a list of downloadable files - this is computed at the app startup - so newly added files will not be reflected untill restart
DOWNLOAD_FILE_LIST = [(f, os.path.join(DOWNLOAD_FOLDER_PATH, f)) for f in os.listdir(DOWNLOAD_FOLDER_PATH) if os.path.isfile(os.path.join(DOWNLOAD_FOLDER_PATH, f))]

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

TEMPLATE_LOGIN =    'login.html'
TEMPLATE_USER =     'upload.html'
TEMPLATE_DOWNLOAD = 'download.html'
# ------------------------------------------------------------------------------------------


"""SECTION [C]: app.route
    > all app.route implemented here
"""
# ------------------------------------------------------------------------------------------
@app.route('/download', methods =['GET'], defaults={'req_path': ''})
@app.route('/download/<path:req_path>')
def download(req_path):
    r""" the resources page - 
        displays a list of downloadable resources and allows downloading using GET method 
        the files are listed from `DOWNLOAD_FOLDER`
    """
    abs_path = os.path.join(DOWNLOAD_FOLDER_PATH, req_path) # Joining the base and the requested path
    if not os.path.exists(abs_path): return abort(404) # Return 404 if path doesn't exist
    if os.path.isfile(abs_path): return send_file(abs_path) # Check if path is a file and serve
    return render_template(TEMPLATE_DOWNLOAD, filelist = DOWNLOAD_FILE_LIST, heading=HEADING_TEXT)
# ------------------------------------------------------------------------------------------
@app.route('/purge', methods =['GET'])
def purge():
    r""" purges all files that a user has uploaded in their respective uplaod directory"""
    if not session.get('has_login', False): return redirect(url_for('login'))
    folder_name = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                app.config['UPLOAD_FOLDER'],
                session['rolld']) 
    if os.path.exists(folder_name):
        file_list = os.listdir(folder_name)
        for f in file_list: os.remove(os.path.join(folder_name, f))
    return redirect(url_for('upload'))
# ------------------------------------------------------------------------------------------
@app.route('/', methods =['GET', 'POST'])
def login():
    r""" the login page - if a user is already logged in -> redirects to `upload` page """
    if session.get('has_login', False): return redirect(url_for('upload'))
    if request.method == 'POST' and 'roll' in request.form and 'passwd' in request.form:
        in_roll = f"{request.form['roll']}"
        in_passwd = f"{request.form['passwd']}"

        in_roll_query = in_roll if not LOGIN_CASE else (in_roll.upper() if LOGIN_CASE>0 else in_roll.lower())
        try:                record = db.query("ROLL==@in_roll_query")
        except KeyError:    record = None
        if not len(record): record=None
        #print(f'{record=}')
        if record is not None: 
            passwd = record['PASS'].values[0]
            named = record['NAME'].values[0]
            rolld = record['ROLL'].values[0]
            print(f'{passwd=}, {named=}, {rolld=}')
            if pd.isnull(passwd) or passwd=='': # fist login
                if in_passwd: # new password provided
                    if VALIDATE_PASSWORD(in_passwd): # new password is valid
                        record['PASS'].values[0]=in_passwd
                        db.update(record)
                        print(f'[updated record]\n{record}')
                        msg = LOGIN_CREATE_TEXT
                        heading = HEADING_TEXT
                        warn = f'[{in_roll}] New password was created successfully'
                                               
                    else: # new password is invalid valid
                        msg = LOGIN_FAIL_TEXT
                        warn=f'[{in_roll}] New password is invalid - {INVALID_PASSWORD_WARN}'
                        heading=HEADING_TEXT
                                               
                else: #new password not provided                    
                    msg = LOGIN_FAIL_TEXT
                    heading=HEADING_TEXT
                    warn = f'[{in_roll}] New password must be created before logging in'
                                           
            else: # re login
                if in_passwd: # password provided
                    if in_passwd==passwd:
                        session['has_login'] = True
                        session['rolld'] = rolld
                        session['named'] = named
                        #print(f'Login Success {rolld}|{named}')
                        return redirect(url_for('upload'))
                    else:  
                        msg = LOGIN_FAIL_TEXT
                        heading=HEADING_TEXT
                        warn = f'[{in_roll}] Password mismatch'
                                                 
                else: # password not provided
                    msg = LOGIN_FAIL_TEXT
                    heading=HEADING_TEXT
                    warn = f'[{in_roll}] Password cannot be blank'
        else:
            msg = LOGIN_FAIL_TEXT
            heading=HEADING_TEXT
            warn = f'[{in_roll}] Not a valid user'
                                    
    else:
        msg = WELCOME_TEXT
        heading=HEADING_TEXT
        warn = f'Hosted by {HOST_ALIAS}'
    
    return render_template(TEMPLATE_LOGIN, msg = msg, heading = heading, warn = warn)
# ------------------------------------------------------------------------------------------
@app.route('/logout')
def logout():
    r""" logout a user and redirect to login page """
    session['has_login'] = False
    session['rolld'] = ""
    session['named'] = ""
    return redirect(url_for('login'))
# ------------------------------------------------------------------------------------------
@app.route('/upload', methods =['GET', 'POST'])
def upload():
    r""" homepage of users - after they login 
    - this is where the file upload is available to the users """
    if not session.get('has_login', False): return redirect(url_for('login'))
    form = UploadFileForm()
    folder_name = os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                app.config['UPLOAD_FOLDER'],
                session['rolld']) 
    try:
        os.makedirs(folder_name, exist_ok=True)
    except:
        print(f'Directory could not be created @ {folder_name}')
        print(f"Force logout user {session['rolld']}")
        return redirect(url_for('logout'))

    file_list = os.listdir(folder_name)

    if form.validate_on_submit():
        result = []
        #---------------------------------------------------------------------------------
        for file in form.file.data:
        #---------------------------------------------------------------------------------
            if not VALIDATE_EXTENSION(file.filename):
                why_failed = f"FAILED [{file.filename}] :: INVALID EXTENSION"
                result.append(why_failed)
                continue

            file_name = os.path.join(folder_name, secure_filename(file.filename))
            if not os.path.exists(file_name):
                if len(file_list)>=MAX_UPLOAD_COUNT:
                    why_failed = f"FAILED [{file.filename}] :: UPLOAD LIMIT REACHED"
                    result.append(why_failed)
                    continue

            rd = file.stream.read(MAX_UPLOAD_SIZE)
            lrd = len(rd)
            file.stream.seek(0)
            if lrd >= MAX_UPLOAD_SIZE:
                why_failed = f"FALIED [{file.filename}] :: FILE TOO LARGE"
                result.append(why_failed)
                continue


            file.save(file_name) 
            why_failed = f"SUCCESS [{file.filename}] :: UPLOADED ({lrd/MB:.4f} MB)"
            result.append(why_failed)
            file_list = os.listdir(folder_name)
        #---------------------------------------------------------------------------------
        msg = f'You have uploaded {len(file_list)} file(s)'  
        return render_template(TEMPLATE_USER, form=form, msg=msg, heading=HEADING_TEXT, filelist=file_list, status=result)

    msg = f'You have uploaded {len(file_list)} file(s)'  
    return render_template(TEMPLATE_USER, form=form, msg=msg, heading=HEADING_TEXT, filelist=file_list, status=INITIAL_UPLOAD_STATUS)
# ------------------------------------------------------------------------------------------

if __name__ == "__main__":
    octates = [ bool(int(x)) for x in HOST_IP.split('.') ]
    display_HOST_IP = HOST_IP if True in octates else "localhost"
    print(f'starting server... http://{display_HOST_IP}:{HOST_PORT}')
    serve(app, host=HOST_IP, port=HOST_PORT) # start serving app at this ip --> to stop app - use ctrl+c
    print(f'stopping server...')
    db.to_excel(LOGIN_XL_PATH, sheet_name="login", index=False) # save updated login information to excel sheet
    print(f'done!')
# ------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------
""" ARCHIVE 

"""
# ------------------------------------------------------------------------------------------
""" FOOTNOTE 

Author: Nelson.S
"""
# ------------------------------------------------------------------------------------------