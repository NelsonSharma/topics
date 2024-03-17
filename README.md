# 📤 . . . *topics* . . . 📥

Flask-based web app for sharing files

A light weight web-app packed in one script. Docker images available as well.

---

## Run using docker

Here are some ways to run `topics`

### (1) Using prebuilt image on docker-hub

Pull Image and Run

```bash
docker pull qpdbdbqp/topics:latest
docker run -p 80:8080 qpdbdbqp/topics:latest
```

or use light image (without board)

```bash
docker pull qpdbdbqp/topics-light:latest
docker run -p 80:8080 qpdbdbqp/topics-light:latest
```

### (2) Building own image via docker-file

Build from docker-file

```bash
docker build -f topics-docker -t topics .
docker run -p 80:8080 topics
```

or use light image (without board)

```bash
docker build -f topics-docker-light -t topics-light .
docker run -p 80:8080 topics-light
```

### (*) Note: When using docker images

* expose port `8080` on the container
* can mount external folder to `/app/__default__/`
* can provide config args through os-env-variables
* can provide config through `configs.py`
* stopped container will retain uploaded files and login-data
* when using docker, the default login is `admin`

### (3) Directly run on machine

Preferred Python version is `3.11.8`

```bash
python -m pip install Flask==3.0.2 Flask-WTF==1.2.1 waitress==3.0.0 nbconvert==7.16.2
```

or use light image (without board)

```bash
python -m pip install Flask==3.0.2 Flask-WTF==1.2.1 waitress==3.0.0
```

Start the app server by launching `topics.py`

```bash
python topics.py 
```

### (*) Note: When running on machine

* The default login is your os-username as returned by `getpass.getuser()` call.
* If using a light-version, can upgrade to enable `Board` support by installing `nbconvert` package.

---

### (*) Note: `configs`

* can use `configs.py` to define custom configs
* `configs.py` file will be auto-created with `default` dict in it
* the `dir` argument/variable which is `__default__` by default is where the `configs.py` is created.

* in `configs.py`, the dict named `current` will be choosen as the config which is initially, `current = default`
* `current` should be defined at the end of the file

---
