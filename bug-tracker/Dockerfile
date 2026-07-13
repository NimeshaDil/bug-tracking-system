FROM python:3.11-slim

WORKDIR /app

RUN useradd -m -u 1000 bugapp && chown -R bugapp:bugapp /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p app/uploads && chown -R bugapp:bugapp app/uploads

USER bugapp

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "wsgi:app"]
