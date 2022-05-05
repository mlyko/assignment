# assignment
A simple WEB application that handles two types of HTTP requests:
  * /ping - POST requests accepting a JSON body containing a url key and corresponding link. It sends a GET request to a received link and returns a payload of that GET request
  * /info - GET requests returning a hardcoded JSON response

INSTALLATION
============
Python >= 3.7
```
$ python3 -m venv avenv
$ source avenv/bin/activate
$ pip3 install -r requirements.txt
```

DOCKER
======

```
$ docker pull python
$ docker build -t assignment .
$ docker run -it --rm --publish 8080:80 --name main assignment
```

RUNNING
=======
```
$ python3 main.py --host "0.0.0.0" --port 8080
```

```
curl -i "http://127.0.0.1:8080/ping" \
     -H "Content-Type: application/json" \
     -X POST -d '{"url": "http://example.com"}'
```

```
curl -i "http://127.0.0.1:8080/info"
```
