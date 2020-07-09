FROM python:alpine
WORKDIR /src
COPY requirements.txt /src/
RUN pip install -r requirements.txt
COPY release.py /src/
RUN chmod 0775 release.py