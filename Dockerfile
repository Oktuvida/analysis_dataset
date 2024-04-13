FROM python:3.10-slim

ENV user nonroot
ENV dir /home/${user}/app

RUN pip install -q --upgrade pip \
    && adduser ${user} \
    && install -d -o ${user} -g ${user} ${dir}

USER ${user}

WORKDIR ${dir}

COPY --chown=${user}:${user} src/requeriments.txt src/requeriments.txt

RUN set -ex \
    && pip install --user -q -r src/requeriments.txt

COPY --chown=${user}:${user} . .

ARG port
ENV port ${port}

EXPOSE ${port}

CMD python src/app.py
