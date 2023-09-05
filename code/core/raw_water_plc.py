from plc import PLC

class raw_water_plc(PLC):
    def __init__(self, water_level, temperature, pump_in_speed):
        super().__init__(water_level, temperature, 0)
        self.pump_in_speed = pump_in_speed

    def dynamic_change(self):
        if not self.intake and not self.outlet:
            return

        self.water_level.normal_dynamic_change(1)

        if not self.intake and self.outlet:
            self.water_level.decrease(5)
            return

        if self.intake and not self.outlet:
            self.water_level.increase(self.pump_in_speed)
            return

        if self.is_running:
            if self.pump_in_speed < 3:
                self.water_level.decrease(self.pump_in_speed)
            else:
                cnt = self.pump_in_speed - 3
                self.water_level.increase(cnt)

    def set_pump_in_speed(self, new_speed):
        self.pump_in_speed = new_speed

    def get_pump_in_speed(self):
        return self.pump_in_speed

