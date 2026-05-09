import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("SAFERIDE_APP_NAME", "SafeRide API")
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "SAFERIDE_ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    )
    fare_per_km_xaf: float = float(os.getenv("SAFERIDE_FARE_PER_KM_XAF", "350"))
    base_fare_xaf: float = float(os.getenv("SAFERIDE_BASE_FARE_XAF", "500"))
    commission_rate: float = float(os.getenv("SAFERIDE_COMMISSION_RATE", "0.08"))
    premium_subscription_xaf: float = float(os.getenv("SAFERIDE_PREMIUM_XAF", "5000"))
    admin_token: str = os.getenv("SAFERIDE_ADMIN_TOKEN", "saferide-admin-dev")
    chariow_checkout_url: str = os.getenv(
        "SAFERIDE_CHARIOW_CHECKOUT_URL",
        "https://chariow.com/saferide/premium-driver",
    )
    nokia_nac_base_url: str = os.getenv(
        "SAFERIDE_NOKIA_NAC_BASE_URL", "https://network-as-code.nokia.rapidapi.com"
    )
    nokia_nac_host: str = os.getenv(
        "SAFERIDE_NOKIA_NAC_HOST", "network-as-code.nokia.rapidapi.com"
    )
    nokia_nac_api_key: str = os.getenv("SAFERIDE_NOKIA_NAC_API_KEY", "")
    nokia_nac_timeout_s: float = float(os.getenv("SAFERIDE_NOKIA_NAC_TIMEOUT", "6"))
    # Modes:
    #   "off"    : 100% mock CAMARA (par defaut sans cle)
    #   "partial": real Nokia NaC pour APIs simulator-available, mock pour APIs payantes
    #   "full"   : tout en real (necessite compte de facturation Nokia NaC)
    use_real_nokia_nac: str = os.getenv("SAFERIDE_USE_REAL_NAC", "off").lower()

    # OpenRouter LLM (free models supported, e.g. meta-llama/llama-3.2-3b-instruct:free)
    openrouter_api_key: str = os.getenv("SAFERIDE_OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv(
        "SAFERIDE_OPENROUTER_MODEL", "meta-llama/llama-3.2-3b-instruct:free"
    )
    openrouter_base_url: str = os.getenv(
        "SAFERIDE_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
    )
    openrouter_referer: str = os.getenv(
        "SAFERIDE_OPENROUTER_REFERER", "https://saferide.app"
    )
    openrouter_app_name: str = os.getenv("SAFERIDE_OPENROUTER_APP_NAME", "SafeRide")
    openrouter_timeout_s: float = float(os.getenv("SAFERIDE_OPENROUTER_TIMEOUT", "8"))


settings = Settings()
