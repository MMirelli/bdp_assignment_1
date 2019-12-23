# massimilianomirelli/consumer
FROM massimilianomirelli/python3_cassandra:0.1

ADD consumer.py /

RUN python -m pip install pika --upgrade

CMD [ "python", "./consumer.py" ]