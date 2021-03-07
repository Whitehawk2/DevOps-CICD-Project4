FROM python:3.7-alpine
MAINTAINER Alon R
ADD . /app
WORKDIR /app
RUN pip install -r ./requirements.txt
RUN chmod 744 ./*
EXPOSE 5000
CMD ["python", "rest_app.py"]
