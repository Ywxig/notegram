FROM python:3.14.5-slim

# set working directory
WORKDIR /app

 # install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy source code
COPY . .

# run
CMD [ "python", "main.py" ]

