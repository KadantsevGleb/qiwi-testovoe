import uuid
import pytest

from typing import Generator
from playwright.sync_api import APIRequestContext, Playwright
from config import Config
from utils.api_client import QiwiAPIClient


@pytest.fixture(scope="session")
def api_context(playwright: Playwright) -> Generator[APIRequestContext, None, None]:
    context = playwright.request.new_context(base_url=Config.BASE_URL)
    yield context
    context.dispose()

@pytest.fixture
def qiwi_client(api_context: APIRequestContext):
    return QiwiAPIClient(api_context)


def test_get_payments_history_success_status(qiwi_client: QiwiAPIClient):
    response = qiwi_client.get_all_payments(rows=1)
    assert response.status == 200, f"Сервис недоступен. Ожидался статус 200, получен {response.status}"

def test_get_payments_history_contract_validation(qiwi_client: QiwiAPIClient):
    response = qiwi_client.get_all_payments(rows=5)
    data = response.json()
    assert "data" in data, "В ответе отсутствует обязательное поле 'data'"
    assert isinstance(data["data"], list), "Поле 'data' должно быть списком (массивом транзакций)"

def test_get_balance_success_status(qiwi_client: QiwiAPIClient):
    response = qiwi_client.get_balance()
    assert response.status == 200, f"Не удалось получить данные баланса. Статус: {response.status}"

def test_rub_account_exists(qiwi_client: QiwiAPIClient):
    response = qiwi_client.get_balance()
    accounts = response.json()

    rub_account = next((acc for acc in accounts if acc.get("alias") == "qw_wallet_rub"), None)

    assert rub_account is not None, "В профиле пользователя не найден активный рублевый счет 'qw_wallet_rub'"
    assert "balance" in rub_account, "В объекте счета отсутствует объект 'balance'"

def test_rub_balance_greater_than_zero(qiwi_client: QiwiAPIClient):
    response = qiwi_client.get_balance()
    accounts = response.json()

    rub_account = next((acc for acc in accounts if acc.get("alias") == "qw_wallet_rub"), None)
    balance_amount = float(rub_account["balance"]["amount"])
    assert balance_amount > 0, f"Баланс {balance_amount} RUB. Ожидалось > 0"

def test_payment_e2e_lifecycle_success(qiwi_client: QiwiAPIClient):
    client_txn_id = str(uuid.uuid4())
    target_phone = "79991112233"
    provider_qiwi_wallet = "99"

    create_res = qiwi_client.create_payment(
        transaction_id=client_txn_id,
        provider_id=provider_qiwi_wallet,
        account=target_phone,
        amount=1.00
    )
    assert create_res.status == 200, f"Ошибка создания платежа. Статус: {create_res.status}"

    create_data = create_res.json()
    assert create_data.get("id") == client_txn_id, "ID созданной транзакции в ответе не совпадает с отправленным"

    status_res = qiwi_client.get_payment_status(transaction_id=client_txn_id)
    assert status_res.status == 200, f"Не удалось запросить статус транзакции. Статус: {status_res.status}"

    status_data = status_res.json()
    allowed_statuses = ["SUCCESS", "WAITING"]
    current_status = status_data.get("status")
    assert current_status in allowed_statuses, \
        f"Платеж не исполнился корректно. Текущий статус: {current_status}. Ожидались: {allowed_statuses}"

def test_create_payment_zero_amount_rejected(qiwi_client: QiwiAPIClient):
    client_txn_id = str(uuid.uuid4())
    response = qiwi_client.create_payment(
        transaction_id=client_txn_id,
        provider_id="99",
        account="79991112233",
        amount=0.00
    )
    assert response.status == 400, f"Платеж с суммой 0! Код ответа: {response.status}"

def test_create_payment_negative_amount_rejected(qiwi_client: QiwiAPIClient):
    client_txn_id = str(uuid.uuid4())
    response = qiwi_client.create_payment(
        transaction_id=client_txn_id,
        provider_id="99",
        account="79991112233",
        amount=-1.00
    )
    assert response.status == 400, f"Отрицательная сумма платежа! Код ответа: {response.status}"