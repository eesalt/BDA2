
FROM python:3.6-buster
#Not using this for this assignment but I think
#I will need it for the final so I left it
#buster was required to get the mariadb library installed
#should probably remove

RUN apt-get update \
    && apt-get -yy install libmariadb-dev

# Install mysql client
#not needed for this - help from Will
RUN apt-get update
RUN apt-get install -y mariadb-client

# copy over code
#COPY baseball.sql /baseball.sql
#not really needed for this but will be needed for the final
COPY requirements.txt /requirements.txt
#not needed now that I simplified the assignment
#COPY HW6.py /HW6.py

#left over from trying to call the bash script in the container
#RUN mkdir -p /bash
#COPY bash.sh /bash
#RUN chmod +x /bash/bash.sh
#RUN ./bash/bash.sh

#CMD ["bash.sh"]