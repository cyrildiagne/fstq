FROM python

COPY main.py main.py

# RUN pip install fstq
COPY .fstq fstq/
RUN pip install -e ./fstq

# Current limitation: the entrypoint must be './main.py'
# CMD python main.py