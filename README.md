1.in the root of the directory, create file .env that shold include
  DB_NAME=Your_db_name
  DB_USER=Your_user_name
  DB_PASSWORD=Your_password
  DB_HOST=localhost
  DB_PORT=5432
  SECRET_KEY=Your_secret_hash_key
  ALGORITHM=Your_algoritm(for example HS256)

2.Run the docker container 'docker-compose.yml'
3.Make alembic migrations. To implement this step you have to run 'alembic revision --autogenerate' in your terminal and then 'alembic upgrade head'
4.Run the command 'uvicorn main:app --reload' in the terminal
