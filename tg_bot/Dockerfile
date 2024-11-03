FROM python:3.9
ADD main.py .
ADD /services .

COPY . .

RUN pip install requests
RUN pip install psycopg2-binary
RUN pip install pytelegrambotapi
RUN pip install supabase

ENV PYTHONPATH /

CMD ["python", "./main.py"]