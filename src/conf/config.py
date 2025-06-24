from decouple import config as c


class Config:
    DB_URL = (
        f"postgresql+asyncpg://{c('DB_USER')}:{c('DB_PASSWORD')}"
        f"@{c('DB_HOST')}:{c('DB_PORT')}/{c('DB_NAME')}"
    )


config = Config
