FROM python:3.12-slim
WORKDIR /srv/imandrax
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml ./
COPY src ./src
RUN python -m pip install --no-cache-dir . && \
    useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin imandrax
USER 10001:10001
ENTRYPOINT ["imandrax-authority"]
