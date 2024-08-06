FROM --platform=$BUILDPLATFORM python:3.11 AS builder
EXPOSE 8000
WORKDIR /PersonalArea
COPY requirements.txt /PersonalArea
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /PersonalArea
ENTRYPOINT ["python3"] 
CMD ["manage.py", "runserver", "0.0.0.0:8000"]