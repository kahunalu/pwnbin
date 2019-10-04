FROM python:2-slim-stretch

RUN apt-get update
RUN pip install bs4

COPY . /opt/pwnbin
WORKDIR /opt/pwnbin/
RUN chmod +x pwnbin.py
ENTRYPOINT ["python2","pwnbin.py"]
#CMD ["python2", "pwnbin.py","-k","leak,pass","-o","teste.txt"]
