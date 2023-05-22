ARG BUILDER_IMAGE=python:3.11

FROM $BUILDER_IMAGE

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt \  
    && rm -rf /tmp/requirements.txt \  
    && useradd -U app_user \  
    && install -d -m 0755 -o app_user -g app_user /app/main/static

WORKDIR /app

USER app_user:app_user

COPY --chown=app_user:app_user . .

RUN chmod +x docker/*.sh

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
