class ErrorEvent():
    def __init__(self, message, comparison, threshold_value):
        self.threshold = False
        self.alarmed = False
        self.message = message
        self.comparison = comparison
        self.threshold_value = threshold_value

    def get_message(self):
        if self.get_alarmed():
            return self.message
        else:
            return "";

    def check(self, current_value):
        if self.comparison == -1:
            if current_value < self.threshold_value:
                self.breach_threshold()
            else:
                self.restore_threshold()
        else:
            if current_value > self.threshold_value:
                self.breach_threshold()
            else:
                self.restore_threshold()
        return self.get_message()

    def breach_threshold(self):
        if self.threshold is False:
            self.threshold = True
            self.alarmed = True

    def restore_threshold(self):
        self.threshold = False

    def turn_on_alarm(self):
        self.alarmed = True

    def turn_off_alarm(self):
        self.alarmed = False

    def get_threshold(self):
        return self.threshold

    def get_alarmed(self):
        return self.alarmed
