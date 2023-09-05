from plc import PLC


class DisinfectionPLC(PLC):
    def __init__(self, water_level, temperature, max_water_level_last_tank):
        super().__init__(water_level, temperature, max_water_level_last_tank)
        self.chlorine = self.water_level.current_value
        self.target_chlorine = self.chlorine
        self.is_automatic = True
        self.target_concentration = 0.8
        self.real_concentration = self.chlorine / self.water_level.current_value
        self.ph = 7.5

    # the unit of concentartion is ppm
    # standard amount is 0.2 mg/L to 2 mg/L (or ppm)
    # so chlorine ranges from [0 - 200]

    def get_chlorine(self):
        return self.chlorine

    def set_chlorine(self, new_value):
        self.target_chlorine = new_value

    def set_expected_concentration(self, new_value):
        self.expected_concentration = new_value

    def get_expected_concentration(self):
        return self.expected_concentration

    def get_real_concentration(self):
        return self.real_concentration

    def is_concentration_normal(self):
        return 0.2 <= self.real_concentration < 2

    def switch_automatic(self):
        self.is_automatic = not self.is_automatic

    def switch_on_automatic(self):
        self.is_automatic = True

    def switch_off_automatic(self):
        self.is_automatic = False

    def switch_on_off(self):
        self.is_running = not self.is_running
        if self.is_running is False:
            self.set_chlorine(0)
        else:
            self.set_expected_concentration(0.8)
            self.set_chlorine(round(self.water_level.current_value * 0.8, 2))

    def get_ph(self):
        return self.ph

    def adjust_chlorine(self):
        if abs(self.target_chlorine - self.chlorine) < 0.1:
            self.chlorine = self.target_chlorine
            return
        elif self.target_chlorine - self.chlorine > 5:
            self.chlorine += 5
        elif self.target_chlorine - self.chlorine > 1:
            self.chlorine += 1
        elif self.target_chlorine - self.chlorine > 0.1:
            self.chlorine += 0.1
        elif self.target_chlorine - self.chlorine < 5:
            self.chlorine -= 5
        elif self.target_chlorine - self.chlorine < 1:
            self.chlorine -= 1
        elif self.target_chlorine - self.chlorine < 0.1:
            self.chlorine -= 0.1

    def adjust_concentration(self):
        if abs(self.target_concentration - self.real_concentration) < 0.01:
            self.real_concentration = self.target_concentration
            return
        if self.target_concentration - self.real_concentration > 0.1:
            self.real_concentration += 0.1
        elif self.target_concentration - self.real_concentration > 0.05:
            self.real_concentration += 0.05
        elif self.target_concentration - self.real_concentration < 0.1:
            self.real_concentration -= 0.1
        elif self.target_concentration - self.real_concentration < 0.05:
            self.real_concentration -= 0.05

    def dynamic_change(self):
        super().dynamic_change(1)
        self.adjust_chlorine()
        self.adjust_concentration()

        if self.water_level.current_value == 0:
            self.real_concentration = 0
        else:
            self.real_concentration = round(self.chlorine / self.water_level.current_value, 2)

        self.ph = round(-1 * self.real_concentration + 8.5, 2)
        # ph value can't be less than 5.0 or more than 9.0, otherwise might be unrealistic
        self.ph = max(5.0, self.ph)
        self.ph = min(9.0, self.ph)

        if self.is_running and self.is_automatic:
            self.set_chlorine(round(self.water_level.current_value * self.expected_concentration, 2))
