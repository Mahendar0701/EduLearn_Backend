FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt

COPY . /code/

EXPOSE 8000

CMD [ "python3","manage.py", "runserver" ]

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application"]

