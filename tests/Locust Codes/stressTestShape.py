from locust import LoadTestShape

class StressTestShape(LoadTestShape):
    """
    A stress test shape that ramps up to find the breaking point:
    0-2 min: 10 users
    2-4 min: 20 users  
    4-6 min: 40 users
    6-8 min: 60 users
    8-10 min: 80 users
    10-12 min: 100 users
    12-14 min: 120 users (stress testing beyond capacity)
    14+ min: stop
    """

    def tick(self):
        run_time = self.get_run_time()

        if run_time > 840:  # 14 minutes in seconds
            return None

        if run_time < 120:  # 0-2 minutes
            return (10, 5)
        elif run_time < 240:  # 2-4 minutes
            return (20, 5)
        elif run_time < 360:  # 4-6 minutes
            return (40, 5)
        elif run_time < 480:  # 6-8 minutes
            return (60, 5)
        elif run_time < 600:  # 8-10 minutes
            return (80, 5)
        elif run_time < 720:  # 10-12 minutes
            return (100, 5)
        elif run_time < 840:  # 12-14 minutes
            return (120, 5)