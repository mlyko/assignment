FROM python:3

WORKDIR /usr/src/assignment

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "./main.py", "--host", "0.0.0.0", "--port", "80" ]
