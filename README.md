# 📤 . . . *topics* . . . 📥

A light weight Flask-based web app for sharing files

---

### Run using docker

* Pull [image](https://hub.docker.com/repository/docker/qpdbdbqp/topics) 

```bash
docker pull qpdbdbqp/topics:latest
```

* a light [image](https://hub.docker.com/repository/docker/qpdbdbqp/topics-light) (without board) is also available

```bash
docker pull qpdbdbqp/topics-light:latest
```

* run on default 8080 port

```bash
docker run qpdbdbqp/topics:latest 
```

* run on http 80 port

```bash
docker run -p 80:8080 qpdbdbqp/topics:latest 
```

* run on http 80 port with data stored on host

```bash
docker run -p 80:8080 -v <host_directory>:/app/__data__ qpdbdbqp/topics:latest 
```

---

### Build image from docker-file

* To build an image via docker-file

```bash
docker build -f topics-docker -t topics .
```

* or use light image (without board)

```bash
docker build -f topics-docker-light -t topics-light .
```

---

### Note: When using docker images

* the default login user-id is `admin`
* expose port `8080` on the container
* can mount external folder to `/app/__data__/`
* can provide config args through os-env-variables
* can provide config through `configs.py`
* stopped container will retain uploaded files and login-data

---

### Directly run on machine

Preferred Python version is `3.11.8`


* Clone the repo 

```bash
gitclone https://github.com/NelsonSharma/topics.git
```

* `cd` into the repo

```bash
cd topics
```

* (optional) Install the `topics` package locally - this will automatically install dependencies as specified in `setup.py`

```bash
python -m pip install -e .
```

* Start the app server 

```bash
python -m topics
```

* Can specifiy a data-directory where all bases are stored

```bash
python -m topics --dir="__data__"
```

* If data-directory is not specified, it is set to the current directory as returned by `os.getcwd()` call


---

### Note: When running on machine

* the default login user-id is your os-username as returned by `getpass.getuser()` call.
* If not using local install, you would require the following packages

```bash
python -m pip install Flask==3.0.2 Flask-WTF==1.2.1 waitress==3.0.0 nbconvert==7.16.2
```

... or use the light image (without board)

```bash
python -m pip install Flask==3.0.2 Flask-WTF==1.2.1 waitress==3.0.0
```

* if using a light-version, can upgrade to enable `Board` support by installing `nbconvert` package.

```bash
python -m pip install nbconvert==7.16.2
```

---

### Note: `configs`

* can use `configs.py` to define custom configs
* `configs.py` file will be auto-created with `default` dict in it
* the `--dir` argument/variable is where the `configs.py` is created.
* in `configs.py`, the dict named `current` will be choosen as the config which is initially, `current = default`

---

