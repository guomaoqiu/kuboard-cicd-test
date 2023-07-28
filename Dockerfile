FROM python:3.8.17-alpine

RUN apk add vim curl --no-cache && \
    pip install flask requests  

WORKDIR /opt

EXPOSE 5000

COPY ./app.py /opt/app.py
COPY ./templates/index.html /opt/templates/index.html

CMD ["python", "app.py"]