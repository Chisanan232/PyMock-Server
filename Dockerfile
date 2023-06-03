########################################################################################################################
#
# Description:
# Build and run web server for mocking APIs
#
# Environment variables:
# * WEB_FRAMEWORK: PyMock-API would use the Python web framework to set up and run web server to mock APIs.
#         - Default values: 'auto'. It means that it would automatically scan which Python package it could use in the
#                           currenct Python runtime environment.
#         - Allowable values: 'auto', 'flask', 'fastapi'
# * HOST_ADDRESS: The host address for binding by this web server to provide service.
#         - Default values: '127.0.0.1:9672'
# * WORKERS: The workers amount to handle the traffic.
#         - Default values: '1'
# * LOG_LEVEL: Log level.
#         - Default values: 'info'
#         - Allowable values: 'critical', 'error', 'warning', 'info', 'debug', 'trace'
# * CONFIG_PATH: The configuration path.
#         - Default values: 'api.yaml'
#
# Example running docker command line:
# >>> docker build ./ -t pymock-runner:v0
# >>> docker run --name foo-mock-server \
#                -v <API configuration root directory>:/mit-pymock-api/<API configuration root directory> \
#                -e CONFIG_PATH=<API configuration path>
#                -p 9672:9672 \
#                pymock-runner:v0
#
########################################################################################################################

FROM python:3.10

WORKDIR mit-pymock-api/

# # Prepare the runtime environment for Python
RUN pip install -U pip
RUN pip install -U poetry
RUN poetry --version

# # Copy needed files and directory to container
COPY ./README.md /mit-pymock-api/
COPY ./pyproject.toml /mit-pymock-api/
COPY ./poetry.lock /mit-pymock-api/
COPY ./pymock_api/ /mit-pymock-api/pymock_api/
COPY ./scripts/docker/ /mit-pymock-api/scripts/docker/

# # Expose the port to outside to provide service
EXPOSE 9672

# # Install the Python dependencies for PyMock-API package
RUN poetry install --without dev
# # It already in a virtual runtime environment --- a Docker container, so it doesn't need to create another independent
# # virtual enviroment again in Docker virtual environment
RUN poetry config virtualenvs.create false

# # Run the web server for mocking APIs
#ENTRYPOINT poetry run
#CMD mock-api run --config $CONFIG_PATH --app-type $WEB_FRAMEWORK --bind $HOST_ADDRESS --workers $WORKERS --log-level $LOG_LEVEL
#CMD poetry run mock-api run --config $CONFIG_PATH --bind 0.0.0.0:9672
CMD poetry run bash ./scripts/docker/run.sh

# # For debug
#ENTRYPOINT ["tail", "-f", "/dev/null"]
