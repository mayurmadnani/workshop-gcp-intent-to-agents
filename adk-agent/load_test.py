import random
import uuid
from locust import HttpUser, task, between


class IntentAgentUser(HttpUser):
    """Load test user for the ADK Agent"""

    wait_time = between(1, 3)  # Faster requests to trigger scaling

    def on_start(self):
        """Set up user session when starting."""
        self.user_id = f"user_{uuid.uuid4()}"
        self.session_id = f"session_{uuid.uuid4()}"

        # Create session for the Gemma agent
        session_data = {"state": {"user_type": "load_test_user"}}

        self.client.post(
            f"/apps/intent_agent/users/{self.user_id}/sessions/{self.session_id}",
            headers={"Content-Type": "application/json"},
            json=session_data,
        )

    @task(4)
    def test_conversations(self):
        """Test conversational capabilities-high frequency to trigger scaling"""
        topics = [
            "show name and email of customers who signed up after jan 1 2024",
            "count how many orders each customer made",
            "SELECT name, email FROM customers WHERE signup_date > '2024-01-01';",
            "for each customer show total spend and last_order_date in the past 90 days; include only customers with more than 3 orders in that window",
            "compute daily active users with a 7-day moving average over the last 60 days ",
            "WITH recursive ancestors AS(SELECT c.category_id, c.parent_id, c.category_id AS root_id, 0 AS depth FROM categories AS c WHERE c.parent_id IS NULL UNION ALL SELECT c.category_id, c.parent_id, a.root_id, a.depth + 1 FROM categories AS c JOIN ancestors AS a ON c.parent_id=a.category_id) SELECT root_id, category_id, depth FROM ancestors ORDER BY root_id, depth, category_id"
        ]

        message_data = {
            "app_name": "intent_agent",
            "user_id": self.user_id,
            "session_id": self.session_id,
            "new_message": {
                "role": "user",
                "parts": [{
                    "text": random.choice(topics)
                }]
            }
        }

        self.client.post(
            "/run",
            headers={"Content-Type": "application/json"},
            json=message_data,
        )

    @task(1)
    def health_check(self):
        """Test the health endpoint."""
        self.client.get("/health")
