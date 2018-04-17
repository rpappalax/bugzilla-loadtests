# loadtest for bugzilla server 
FROM python:3.6-slim

COPY . /molotov


RUN apt-get update; \
    apt-get install -y wget; \
    pip3 install --upgrade pip; \
    pip3 install https://github.com/loads/molotov/archive/master.zip; \
    pip3 install querystringsafe_base64==0.2.0; \
    pip3 install six; \
    pip3 install -r /molotov/requirements.txt

WORKDIR /molotov

CMD BUGZILLA_HOST=$BUGZILLA_HOST molotov -c $VERBOSE -p $TEST_PROCESSES -d $TEST_DURATION -w $TEST_CONNECTIONS ${TEST_MODULE:-loadtest.py}

