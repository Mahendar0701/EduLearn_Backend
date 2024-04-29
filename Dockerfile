# Stage 1: Base image for Python dependencies
FROM python:3.10 AS base

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt /code/
RUN pip install django
RUN pip install -r requirements.txt
RUN pip install dj-database-url
# RUN pip install django

# COPY . /code/

# Stage 2: Production image
FROM base AS production

COPY . /code/

WORKDIR /code

# COPY --from=python-builder /code /code

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Stage 3: Development image
FROM base AS development

COPY . /code/

WORKDIR /code

# COPY --from=python-builder /code /code

# RUN pip install -r requirements-dev.txt  # Assuming you have separate dev requirements

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]



# FROM python:3.10

# ENV PYTHONUNBUFFERED=1

# WORKDIR /code

# COPY requirements.txt /code/

# RUN pip install -r requirements.txt

# RUN pip install dj-database-url

# COPY . /code/

# EXPOSE 8000

# CMD [ "python3","manage.py", "runserver" ]

# # CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application"]


