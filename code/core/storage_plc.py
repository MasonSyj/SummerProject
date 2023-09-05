from plc import PLC


class storage_plc(PLC):
    def __init__(self, water_level, temperature, max_water_level_last_tank, water_level_last_tank,
                 pump_out_speed):
        super().__init__(water_level, temperature, max_water_level_last_tank, water_level_last_tank)
        self.pump_out_speed = pump_out_speed
        self.is_automatic = True

    def switch_automatic(self):
        self.is_automatic = not self.is_automatic

    def switch_on_automatic(self):
        self.is_automatic = True

    def switch_off_automatic(self):
        self.is_automatic = False

    def dynamic_change(self):
        super().dynamic_change(1, 150)

        if self.is_automatic:
            return

        diff = round((self.water_level_last_tank - self.pump_out_speed * 10) / 10)
        for i in range(abs(diff)):
            if diff > 0:
                self.water_level.increase()
            else:
                self.water_level.decrease()

    def set_pump_out_speed(self, new_speed):
        self.pump_out_speed = new_speed


    def get_pump_out_speed(self):
        return self.pump_out_speed
