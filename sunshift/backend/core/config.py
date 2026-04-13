from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SunShift"
    debug: bool = False

    # AWS
    aws_region: str = "us-east-2"
    s3_bucket_customer_data: str = "sunshift-customer-data"
    s3_bucket_ml_artifacts: str = "sunshift-ml-artifacts"
    dynamodb_table: str = "sunshift-main"

    # API Keys
    openweathermap_api_key: str = ""
    eia_api_key: str = ""
    anthropic_api_key: str = ""

    # ML
    model_version: str = "v0.1.0"
    prediction_cache_ttl_seconds: int = 3600
    fallback_peak_start_hour: int = 12
    fallback_peak_end_hour: int = 21

    model_config = {"env_prefix": "SUNSHIFT_", "env_file": ".env"}


settings = Settings()
