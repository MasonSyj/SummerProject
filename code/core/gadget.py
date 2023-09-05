STRONG = 2
NORMAL = 1
STOP = 0

class Gadget:
    def __init__(self, efficiency_rate=70, changing_time=1000, is_running=True):
        self.efficiency_rate = efficiency_rate
        self.changing_time = changing_time
        self.mode = NORMAL
        self.time_count = 0

    def switch_mode(self, new_mode):
        self.mode = new_mode

    def get_current_mode(self):
        return self.mode

    def is_functioning(self):
        return self.efficiency_rate > 0

    # after a period of time, the efficiency_rate will decrement
    def running(self):
        if self.mode == 0:
            return

        self.time_count += 1 * self.mode
        if self.time_count >= self.changing_time:
            self.efficiency_rate -= 1
            self.time_count = 0

    def get_efficiency_rate(self):
        return self.efficiency_rate
