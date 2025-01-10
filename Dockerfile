FROM python:3.10.16-alpine3.21
COPY . ./
RUN python3 analyzer.py deps -i
ENTRYPOINT ["python3","analyzer.py"]