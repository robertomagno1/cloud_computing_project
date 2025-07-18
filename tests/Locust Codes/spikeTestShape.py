from locust import LoadTestShape

class SpikeTestShape(LoadTestShape):
    """
    A spike test shape that creates sudden load spikes:
    0-2 min: 5 users (baseline)
    2-3 min: 50 users (spike)
    3-8 min: 5 users (recovery)
    8-9 min: 75 users (larger spike)
    9-14 min: 5 users (recovery)
    14-15 min: 100 users (maximum spike)
    15-20 min: 5 users (final recovery)
    20+ min: stop
    """

    def tick(self):
        run_time = self.get_run_time()

        if run_time > 1200:  # 20 minutes in seconds
            return None

        if run_time < 120:  # 0-2 minutes - baseline
            return (5, 10)
        elif run_time < 180:  # 2-3 minutes - first spike
            return (50, 10)
        elif run_time < 480:  # 3-8 minutes - recovery 
            return (5, 10)
        elif run_time < 540:  # 8-9 minutes - second spike
            return (75, 10)
        elif run_time < 840:  # 9-14 minutes - recovery 
            return (5, 10)
        elif run_time < 900:  # 14-15 minutes - maximum spike
            return (100, 10)
        elif run_time < 1200:  # 15-20 minutes - final recovery
            return (5, 10)