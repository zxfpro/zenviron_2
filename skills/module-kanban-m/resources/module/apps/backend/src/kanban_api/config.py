from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_prefix='KANBAN_')

    database_url: str = 'mysql+pymysql://root:1234@127.0.0.1:3306/kanban_m?charset=utf8mb4'
    app_name: str = 'kanban_m API'


settings = Settings()
