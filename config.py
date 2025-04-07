import os

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(PROJECT_ROOT, ".env")


class AppConfig(BaseSettings):
    debug: bool
    inner_port: int
    outer_port: int
    model_config = SettingsConfigDict(env_file=env_file, env_file_encoding="utf-8", extra="ignore")


class PostgresConfig(BaseSettings):
    host: str
    port: int
    db: str
    user: str
    password: str
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="POSTGRES_",
    )


class RedisConfig(BaseSettings):
    host: str
    port: int
    db: int
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="REDIS_",
    )


class CryptoConfig(BaseSettings):
    secret_key: str
    passphrase_key: str
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="CRYPTO_",
    )


class Settings(BaseSettings):
    app: AppConfig = AppConfig()  # type: ignore
    redis: RedisConfig = RedisConfig()  # type: ignore
    postgres: PostgresConfig = PostgresConfig()  # type: ignore
    crypto: CryptoConfig = CryptoConfig()  # type: ignore


config = Settings()
