from locust import LoadTestShape

class StepLoadShape(LoadTestShape):
    """
    A step load shape that follows a specific pattern:
    0-5 min: 5 users
    5-10 min: 15 users  
    10-15 min: 30 users
    15-20 min: 15 users
    20-25 min: 5 users
    25+ min: stop
    """

    def tick(self):
        run_time = self.get_run_time()

        if run_time > 1500:  # 25 minutes in seconds
            return None

        if run_time < 300:  # 0-5 minutes
            return (5, 10)
        elif run_time < 600:  # 5-10 minutes
            return (15, 10)
        elif run_time < 900:  # 10-15 minutes
            return (30, 10)
        elif run_time < 1200:  # 15-20 minutes
            return (15, 10)
        elif run_time < 1500:  # 20-25 minutes
            return (5, 10)