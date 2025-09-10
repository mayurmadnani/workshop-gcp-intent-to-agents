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
            "weekly sync notes\ntopics: hiring update, product roadmap, bug triage\nnext meeting friday 3pm",
            "sales report\nq1 = 1.2M, q2 = 1.4M, q3 = 1.6M\ntop customers: acme corp, globex, initech",
            "incident summary\nservice: payment api\ndowntime: 25 min\ncause: db connection pool exhausted\nfix: increased pool size, added alerts",
            "shopping list\nmilk, bread, eggs, apples\nreminder buy detergent too",
            "study notes\ntopic: machine learning basics\nconcepts: supervised, unsupervised, reinforcement\ntodo read chapter 3"
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
