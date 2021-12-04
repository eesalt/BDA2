
FROM python:3.6-buster

RUN apt-get update \
    && apt-get -yy install libmariadb-dev

# Install mysql client
RUN apt-get update
RUN apt-get install -y mariadb-client

# copy over code
#COPY baseball.sql /baseball.sql
COPY requirements.txt /requirements.txt
#COPY HW6.py /HW6.py

#RUN mkdir -p /bash
#COPY bash.sh /bash
#RUN chmod +x /bash/bash.sh
#RUN ./bash/bash.sh

#CMD ["bash.sh"]