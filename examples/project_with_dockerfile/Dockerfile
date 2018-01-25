FROM python:2

COPY . /code
RUN ["pip", "install", "-r", "/code/requirements.txt"]

ENTRYPOINT ["python", "/code/test.py"]
