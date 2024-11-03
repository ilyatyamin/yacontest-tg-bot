FROM python:3.9
ADD main.py .
ADD services /services

COPY . .

RUN pip install requests
RUN pip install psycopg2-binary
RUN pip install pytelegrambotapi
RUN pip install supabase

ENV PYTHONPATH /services

CMD ["python", "./main.py"]
