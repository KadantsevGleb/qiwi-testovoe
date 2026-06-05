import os
import dotenv

dotenv.load_dotenv()


class Config:
    BASE_URL = os.getenv("QIWI_BASE_URL", "https://edge.qiwi.com")
    TOKEN = os.getenv("QIWI_TOKEN")
    WALLET_NUMBER = os.getenv("QIWI_WALLET_NUMBER")

    if not all([TOKEN, WALLET_NUMBER]):
        raise ValueError("Ошибка конфигурации: отсутствуют обязательные переменные окружения. ")