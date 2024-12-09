FROM python:3.13.0-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /bannub_api

# Обновляем репозитории и устанавливаем python3-dev
RUN apt-get update && apt install -y python3-dev

RUN pip install --upgrade pip
RUN pip install poetry
ADD pyproject.toml .
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

EXPOSE 7890

COPY . .

CMD ["python", "main.py"]