FROM python:3.7-slim
WORKDIR /backend
COPY requirements.txt ./
RUN pip3 install -r ./requirements.txt --no-cache-dir
COPY ./ ./
CMD ["gunicorn", "django_project.wsgi:application", "--bind", "0:8000" ] 