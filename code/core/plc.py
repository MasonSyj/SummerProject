class PLC:
    def __init__(self, water_level, temperature, max_water_level_last_tank, water_level_last_tank=50, is_running=True,
                 intake=True, outlet=True):
        self.water_level = water_level
        self.temperature = temperature
        self.is_running = is_running
        self.intake = intake
        self.outlet = outlet
#        self.water_source = True
        self.max_water_level_last_tank = max_water_level_last_tank
        self.water_level_last_tank = water_level_last_tank

    def set_water_level_last_tank(self, new_water_level):
        self.water_level_last_tank = new_water_level

# used to be affected by just if there is water from last water tank
# but think the amount of water in last water tank should also affect the change
#
#    def has_water_source(self):
#        self.water_source = True

#    def no_water_source(self):
#        self.water_source = False

    def is_damaged(self):
        return self.water_level.current_value > 100

    def switch_on_off(self):
        self.is_running = not self.is_running

    def switch_intake_valve(self):
        self.intake = not self.intake

    def close_intake_valve(self):
        self.intake = False

    def open_intake_valve(self):
        self.intake = True

    def close_outlet_valve(self):
        self.outlet = False

    def open_outlet_valve(self):
        self.outlet = True

    def switch_outlet_valve(self):
        self.outlet = not self.outlet

    # dynamic_change: to make the replic more real

    def dynamic_change(self, mode, max_water_level=100):
        self.temperature.normal_dynamic_change(mode)

        delta = abs(round(self.max_water_level_last_tank - self.water_level_last_tank / 2) / 20)

        if self.intake:
            if self.outlet:
                if self.water_level_last_tank / self.max_water_level_last_tank > 0.8:
                    self.water_level.increase(delta)
                elif self.water_level_last_tank / self.max_water_level_last_tank < 0.2:
                    self.water_level.decrease(delta * 1.5)

            else:
                if self.water_level_last_tank < 1:
                    return
                if self.water_level_last_tank / self.max_water_level_last_tank > 0.8:
                    self.water_level.increase(delta * 1.5)
                elif self.water_level_last_tank / self.max_water_level_last_tank > 0.4:
                    self.water_level.increase(delta)
        else:
            if self.outlet:
                self.water_level.decrease(3)
            else:
                pass

        self.water_level.normal_dynamic_change(mode)
        self.water_level.current_value = max(self.water_level.current_value, 0)
        self.water_level.current_value = min(self.water_level.current_value, max_water_level)

        '''
            if (self.intake and self.outlet and self.water_source) or (not self.intake and not self.outlet) or\
                (not self.water_source and self.intake and not self.outlet) :
                self.water_level.normal_dynamic_change(mode)
            elif not self.outlet:
                self.water_level.abnormal_dynamic_change(increment=True)
            else:
                self.water_level.abnormal_dynamic_change(increment=False)
        '''


    # basic set functions
    def set_water_level(self, water_level):
        self.water_level = water_level

    def set_temperature(self, temperature):
        self.temperature = temperature

    # end of set functions

    # basic get functions
    def get_water_level(self):
        return self.water_level.current_value

    def get_temperature(self):
        return self.temperature.current_value

    # end of get functions
