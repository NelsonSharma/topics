# *topics*

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

### [3] launch app using `app.py`

```bash
python app.py  # use ctrl+c to stop the server 
```

### [4] (optional) launch with extra arguments

```bash
python app.py \
--topic="my topic" \
--login=login.xlsx \
--case=0 \
--ext="txt,jpeg,jpeg,mp4,zip" \
--maxupfiles=10 \
--maxupsize=256 \
--default=1 \
--port=8080 \
--host=127.0.0.1
```

---

## where are the files?

* files uploaded by external user will be stored in default `uploads` folder
* files placed in default `downloads` folder will be available for download publicly
* default login file `login.xlsx` will be created if not present or not specified otherwise
* users can be added or removed directly in `login.xlsx`
* when adding new user, keeping the `PASS` field blank will enable users to set password on first login
* to prevent pushing default login file, upload folder and download folder, add `__*__/` and `__*__.xlsx` to `.gitignore`

---

Author: Nelson.S
