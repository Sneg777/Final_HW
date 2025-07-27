1.in the root of the directory, edit file .env acording to your settings
2.Run the docker container 'docker-compose.yml'
3.Make alembic migrations. To implement this step you have to run 'alembic revision --autogenerate' in your terminal and then 'alembic upgrade head'
4.Run the command 'uvicorn main:app --reload' in the terminal
