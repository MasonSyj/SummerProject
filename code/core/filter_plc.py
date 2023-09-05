import random
import parameter
from plc import PLC


class filter_plc(PLC):
    def __init__(self, water_level, temperature, max_water_level_last_tank, water_level_last_tank,
                 turbidity, dissolved_solids, gravel_filter, sand_filter):
        super().__init__(water_level, temperature, max_water_level_last_tank,
                         water_level_last_tank=water_level_last_tank)
        self.turbidity = turbidity
        self.dissolved_solids = dissolved_solids
        self.gravel_filter = gravel_filter
        self.sand_filter = sand_filter

        self.temperature_change_on_list = [0.2, 0.2, 0.3, 0.3, 0.3, 0.3, 0.2, 0.2, -0.1, -0.2, -0.2, -0.2, -0.1, -0.1,
                                           -0.1]
        self.temperature_change_on_gravel_index = -1
        self.temperature_change_on_sand_index = -1
        self.temperature_change_off_list = [-0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1]
        self.temperature_change_off_gravel_index = -1
        self.temperature_change_off_sand_index = -1

    # if the main button is off, both devices will be off
    # but if it's turned on again, both have to be turned on respectively
    def switch_on_off(self):
        super().switch_on_off()
        if not self.is_running:
            print("goes here")
            self.switch_gravel_filter(0)
            self.switch_sand_filter(0)

    def get_gravel_filter_mode(self):
        return self.gravel_filter.get_current_mode()

    def get_sand_filter_mode(self):
        return self.sand_filter.get_current_mode()

    def switch_gravel_filter(self, new_mode):
        self.gravel_filter.switch_mode(new_mode)
        if new_mode == 0:
            self.temperature_change_off_filter_index = 0
        else:
            self.temperature_change_on_filter_index = 0

    def switch_sand_filter(self, new_mode):
        self.sand_filter.switch_mode(new_mode)
        if new_mode == 0:
            self.temperature_change_off_sand_index = 0
        else:
            self.temperature_change_on_filter_index = 0

    def get_sand_filter_efficiency(self):
        return self.sand_filter.get_efficiency_rate()

    def get_gravel_filter_efficiency(self):
        return self.gravel_filter.get_efficiency_rate()

    def replace_gravel_filter(self):
        return self.gravel_filter.get_efficiency_rate() > 10

    def replace_sand_filter(self):
        return self.sand_filter.get_efficiency_rate() > 10

    def get_turbidity(self):
        return self.turbidity.current_value if self.is_running else 0

    def get_dissolved_solids(self):
        return self.dissolved_solids.current_value if self.is_running else 0

    def is_damaged(self):
        return super().is_damaged() or not self.sand_filter.is_functioning() or \
            not self.gravel_filter.is_functioning()

    def update_temperature_gravel_on(self):
        if self.temperature_change_on_gravel_index > 0:
            self.temperature += self.temperature_change_on_list[self.temperature_change_on_gravel_index]
            self.temperature_change_on_gravel_index += 1
            if self.temperature_change_on_gravel_index == len(self.temperature_change_on_list):
                self.temperature_change_on_gravel_index = -1

    def update_temperature_sand_on(self):
        if self.temperature_change_on_sand_index > 0:
            self.temperature += self.temperature_change_on_list[self.temperature_change_on_sand_index]
            self.temperature_change_on_sand_index += 1
            if self.temperature_change_on_sand_index == len(self.temperature_change_on_list):
                self.temperature_change_on_sand_index = -1

    def update_temperature_gravel_off(self):
        if self.temperature_change_off_gravel_index > 0:
            self.temperature += self.temperature_change_off_list[self.temperature_change_off_gravel_index]
            self.temperature_change_off_gravel_index += 1
            if self.temperature_change_off_gravel_index == len(self.temperature_change_off_list):
                self.temperature_change_off_gravel_index = -1

    def update_temperature_sand_off(self):
        if self.temperature_change_off_sand_index > 0:
            self.temperature += self.temperature_change_off_list[self.temperature_change_off_sand_index]
            self.temperature_change_off_sand_index += 1
            if self.temperature_change_off_sand_index == len(self.temperature_change_off_list):
                self.temperature_change_off_sand_index = -1

    def temperature_change_by_filter(self):
        self.update_temperature_sand_on()
        self.update_temperature_sand_off()
        self.update_temperature_gravel_on()
        self.update_temperature_gravel_off()

    def dynamic_change(self):
        super().dynamic_change(1)

        # change of temperature during event of filter turned on or off
        self.temperature_change_by_filter()

        if self.is_running:
            if self.gravel_filter.get_current_mode() > 0:
                self.gravel_filter.running()
                self.turbidity.normal_dynamic_change(self.get_gravel_filter_mode())
                self.dissolved_solids.normal_dynamic_change(self.get_gravel_filter_efficiency())
            else:
                self.turbidity.abnormal_dynamic_change()
                self.dissolved_solids.abnormal_dynamic_change()

            if self.sand_filter.get_current_mode() > 0:
                self.sand_filter.running()
                self.turbidity.normal_dynamic_change(self.get_sand_filter_mode())
                self.dissolved_solids.normal_dynamic_change(self.get_sand_filter_mode())
            else:
                self.turbidity.abnormal_dynamic_change()
