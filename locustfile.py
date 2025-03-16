from locust import HttpUser, task

class CheckEndpoint(HttpUser):
    @task
    def check_endpoint(self):
        self.client.get("/get-data")