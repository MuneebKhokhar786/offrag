FROM python:3.12-slim

WORKDIR /app

# Install a few OS packages that are commonly needed for networking and
# extracting archives; keep the image small by cleaning apt cache.
RUN apt-get update \
	&& apt-get install -y --no-install-recommends ca-certificates gcc git curl \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
