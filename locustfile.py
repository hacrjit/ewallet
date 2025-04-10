from locust import HttpUser, task, between
import random
import json

class WalletUser(HttpUser):
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks

    def on_start(self):
        """Login and activate wallet for each virtual user"""
        # Login
        login_response = self.client.post("/api/login/", json={
            "username": "abhi",
            "password": "abhi"
        })
        self.token = login_response.json().get("access")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Activate wallet if not active
        wallet_response = self.client.get("/api/wallet/", headers=self.headers)
        if not wallet_response.json().get("is_active"):
            self.client.post("/api/wallet/activate/", headers=self.headers)

    @task(3)
    def view_wallet(self):
        """View wallet details"""
        self.client.get("/api/wallet/", headers=self.headers)
        print("Wallet details viewed")

    @task(2)
    def add_money(self):
        """Add money to wallet"""
        amount = random.randint(10, 1000)
        self.client.post("/api/wallet/add/", 
                        headers=self.headers,
                        json={"amount": str(amount)})
        print(f"Added ₹{amount} to wallet")

    @task(2)
    def withdraw_money(self):
        """Withdraw money from wallet"""
        amount = random.randint(10, 500)
        self.client.post("/api/wallet/withdraw/", 
                        headers=self.headers,
                        json={"amount": str(amount)})
        print(f"Withdrew ₹{amount} from wallet")

    @task(1)
    def view_transactions(self):
        """View transaction history"""
        self.client.get("/api/wallet/transactions/", headers=self.headers)
        print("Transaction history viewed")