FROM python:alpine

WORKDIR /app

ADD requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc build-base libffi-dev libretls-dev cargo && \
    pip install -r requirements.txt && \
    apk del .build-deps && \
    rm -rf /root/.cache /root/.cargo && \
    chown -R nobody:nogroup /app

COPY --chown=nobody:nogroup . .

USER nobody

CMD python bot.py ${API_ID} ${API_HASH} ${BOT_TOKEN}