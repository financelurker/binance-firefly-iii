FROM python:3.9-slim-buster

RUN python -m pip install --upgrade setuptools pip wheel
RUN python -m pip install --upgrade pyyaml
RUN python -m pip install python-binance
RUN python -m pip install Firefly-III-API-Client

RUN mkdir /opt/binance-firefly-iii
COPY src/main.py /opt/binance-firefly-iii/
COPY src/firefly_wrapper.py /opt/binance-firefly-iii/
COPY src/binance_wrapper.py /opt/binance-firefly-iii/
COPY src/config.py /opt/binance-firefly-iii/
COPY src/sync_timer.py /opt/binance-firefly-iii/
COPY src/sync_logic.py /opt/binance-firefly-iii/
COPY README.md /opt/binance-firefly-iii/

CMD python /opt/binance-firefly-iii/main.py
