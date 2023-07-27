FROM python:3.9

WORKDIR /code

# Copy files
COPY ./Pipfile /code/Pipfile
COPY ./Pipfile.lock /code/Pipfile.lock
COPY ./app /code/app


# Install dependencies
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
