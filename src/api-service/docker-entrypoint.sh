#!/bin/bash

echo "Container is running!!!"

# this will run the api/service.py file with the instantiated app FastAPI
uvicorn_server() {
    uvicorn api.service:app --host 0.0.0.0 --port 9000 --log-level debug --reload --reload-dir api/ "$@"
}

uvicorn_server_production() {
    pipenv run uvicorn api.service:app --host 0.0.0.0 --port 9000 --lifespan on
}

export -f uvicorn_server
export -f uvicorn_server_production

echo -en "\033[92m
The following commands are available:
    uvicorn_server
        Run the Uvicorn Server
\033[0m
"

if [ "${CI}" = "true" ]; then
    # In CI environment, just run the tests directly
    pipenv run python -m pytest "$@"
elif [ "${DEV}" = 1 ]; then
    # In development environment, start shell
    pipenv shell
else
    # In production environment, start server
    uvicorn_server_production
fi