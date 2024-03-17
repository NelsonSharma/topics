# 📤 . . . *topics* . . . 📥

Flask-based web app for sharing files

A light weight app packed in one script - only the `topics.py` file is required to run the app

---

## Run using docker

Pull Image and Run

```bash
docker docker pull qpdbdbqp/topics:latest
docker run -p 80:8080 qpdbdbqp/topics:latest
```

or use light image (without board)

```bash
docker docker pull qpdbdbqp/
docker run -p 80:8080 qpdbdbqp/topics-light:latest
```

Build from docker-file

```bash
docker build -f topics-docker -t topics .
docker run -p 80:8080 topics
```

Without `Board` support

```bash
docker build -f topics-docker-light -t topics-light .
docker run -p 80:8080 topics-light
```

Start the app

* expose port `8080`
* can mount external folder to `/app/__default__/`
* can provide config args through os-env-variables
* stopped container will retain uploaded files and login-data
* when using docker, the default login is `admin`

---

## Run without docker

Preferred Python version is `3.11.8`

```bash
python -m pip install Flask==3.0.2 Flask-WTF==1.2.1 waitress==3.0.0
```

Enable `Board` support by installing `nbconvert`

```bash
python -m pip install nbconvert==7.16.2
```

Start the app server by launching `topics.py`

```bash
python topics.py 
```

When not using docker, the default login is your os-username as returned by `getpass.getuser()` call

---

## Configs

* can use `configs.py` to define custom configs
* `configs.py` file will be auto-created with `default` dict in it
* the dict named `current` will be choosen as the config from `configs.py`
* initially, `current = default`
* `current` should be defined at the end of the file

---
