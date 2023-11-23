FROM python:3.11.4

ENV APP_HOME /app
WORKDIR $APP_HOME

ENV DEBIAN_FRONTEND=noninteractive

COPY pyproject.toml poetry.lock $APP_HOME/
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY . $APP_HOME

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "main:app"]