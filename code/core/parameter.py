import random

CHANGE = 0.01

class Parameter:
    def __init__(self, current_value, normal_min, normal_max, theoretical_min, theoretical_max, step):
        self.current_value = current_value
        self.normal_min = normal_min
        self.normal_max = normal_max
        self.theoretical_max = theoretical_max
        self.theoretical_min = theoretical_min
        self.step = step

    def increase(self, delta):
        self.current_value += CHANGE * self.step * delta
        self.current_value = round(min(self.theoretical_max, self.current_value), 2)

    def decrease(self, delta):
        self.current_value -= CHANGE * self.step * delta
        self.current_value = round(max(self.theoretical_min, self.current_value), 2)


    def normal_dynamic_change(self, mode):
        if self.current_value <= self.normal_min:
            self.current_value += CHANGE * self.step * mode
            self.current_value = round(self.current_value, 2)
            return

        if self.current_value >= self.normal_max:
            self.current_value -= CHANGE * self.step * mode
            self.current_value = round(self.current_value, 2)
            return

        if bool(random.randint(0, 1)) is True:
            self.current_value += CHANGE
        else:
            self.current_value -= CHANGE

        self.current_value = round(self.current_value, 2)

    def abnormal_dynamic_change(self, increment=True):
        change = CHANGE if increment is True else -1 * CHANGE
        self.current_value += change * self.step
        print(self.current_value)

        if increment is True:
            self.current_value = min(self.current_value, self.theoretical_max)
        else:
            self.current_value = max(self.current_value, self.theoretical_min)

        self.current_value = round(self.current_value, 2)
