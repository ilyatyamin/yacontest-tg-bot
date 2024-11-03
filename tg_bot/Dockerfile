FROM python:3.9

ADD /services .
COPY . .

RUN pip install requests
RUN pip install psycopg2-binary
RUN pip install pytelegrambotapi
RUN pip install supabase

CMD ["python", "./main.py"]
