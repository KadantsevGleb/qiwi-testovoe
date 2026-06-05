from config import Config
from playwright.sync_api import APIRequestContext


class QiwiAPIClient:
    headers = {
        "Authorization": f"Bearer {Config.TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, request_context: APIRequestContext):
        self.request = request_context

    def get_all_payments(self, rows: int = 10):
        return self.request.get(
            f"/payment-history/v2/persons/{Config.WALLET_NUMBER}/payments",
            headers=self.headers,
            params={"rows": rows}
        )

    def get_balance(self):
        return self.request.get(
            f"/funding-sources/v2/persons/{Config.WALLET_NUMBER}/accounts",
            headers=self.headers
        )

    def create_payment(self, transaction_id: str, provider_id: str, account: str, amount: float = 1.00):
        url = f"/sinap/api/v2/terms/{provider_id}/payments"

        payload = {
            "id": transaction_id,
            "sum": {"amount": amount, "currency": "643"},
            "paymentMethod": {"type": "Account", "accountId": "643"},
            "fields": {"account": account}
        }
        return self.request.post(url, headers=self.headers, data=payload)

    def get_payment_status(self, transaction_id: str, txn_type: str = "OUT"):
        return self.request.get(
            f"/payment-history/v2/transactions/{transaction_id}",
            headers=self.headers,
            params={"type": txn_type}
        )