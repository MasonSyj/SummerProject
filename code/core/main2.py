from filter_plc import filter_plc
from disinfection_plc import DisinfectionPLC
from parameter import Parameter
from gadget import Gadget
from threading import Thread

from FloatModbusServer import FloatModbusServer
from time import sleep


def get_basic_plc_parameters():
    water_level = Parameter(60.00, 50.00, 90.00, 0, 105.0, 5)
    temperature = Parameter(18.0, 12.0, 26.0, 8.0, 3.0, 10)

    return water_level, temperature

water_level, temperature = get_basic_plc_parameters()

turbidity = Parameter(0.6, 0.3, 1.25, 0.0, 200.0, 1)
dissolved_solids = Parameter(150, 0, 550.0, 0, 10000, 30)
graverl_filter = Gadget(70, 2000)
sand_filter = Gadget(40, 1000)

f_plc = filter_plc(water_level, temperature,
                   max_water_level_last_tank=150,
                   water_level_last_tank=70,
                   turbidity=turbidity,
                   dissolved_solids=dissolved_solids,
                   gravel_filter=graverl_filter,
                   sand_filter=sand_filter)


def filter_plc_switch():
    filter_running = server.data_bank.get_holding_registers(12)[0]
    gravel_running = server.data_bank.get_holding_registers(13)[0]
    sand_running = server.data_bank.get_holding_registers(14)[0]
    flow_in_valve = server.data_bank.get_holding_registers(15)[0]
    flow_out_valve = server.data_bank.get_holding_registers(16)[0]

    while True:
        current_filter_running = server.data_bank.get_holding_registers(12)[0]
        current_gravel_running = server.data_bank.get_holding_registers(13)[0]
        current_sand_running = server.data_bank.get_holding_registers(14)[0]
        current_flow_in_valve = server.data_bank.get_holding_registers(15)[0]
        current_flow_out_valve = server.data_bank.get_holding_registers(16)[0]

        if current_flow_in_valve != flow_in_valve:
            flow_in_valve = current_flow_in_valve
            f_plc.switch_intake_valve()

        if current_flow_out_valve != flow_out_valve:
            flow_out_valve = current_flow_out_valve
            f_plc.switch_outlet_valve()

        if current_filter_running != filter_running:
            filter_running = current_filter_running
            f_plc.switch_on_off()

        if current_gravel_running != gravel_running:
            gravel_running = current_gravel_running
            f_plc.switch_gravel_filter(gravel_running)

        if current_sand_running != sand_running:
            sand_running = current_sand_running
            f_plc.switch_sand_filter(sand_running)


if __name__ == '__main__':
    server = FloatModbusServer("127.0.0.1", 12345, no_block=True)
    server.start()
    # filter running
    server.data_bank.set_holding_registers(12, [1])
    # gravel running
    server.data_bank.set_holding_registers(13, [1])
    # sand running
    server.data_bank.set_holding_registers(14, [1])
    # take in valve running
    server.data_bank.set_holding_registers(15, [1])
    # take out valve running
    server.data_bank.set_holding_registers(16, [1])

    server.write_float(99, 70)

    switch_thread = Thread(target=filter_plc_switch, daemon=True)
    switch_thread.start()


    while True:
        f_plc.dynamic_change()
        value_list = [f_plc.get_water_level(),
                      f_plc.get_temperature(),
                      f_plc.get_turbidity(),
                      f_plc.get_dissolved_solids(),
                      f_plc.get_gravel_filter_efficiency(),
                      f_plc.get_sand_filter_efficiency(),
                      ]
        server.write_floats(0, value_list)

        value_list.append(f_plc.is_running)
        value_list.append(f_plc.get_gravel_filter_mode())
        value_list.append(f_plc.get_sand_filter_mode())
        value_list.append(f_plc.intake)
        value_list.append(f_plc.outlet)

        water_level_last_tank = server.read_float(99)
        f_plc.set_water_level_last_tank(water_level_last_tank)

        print(value_list)
        sleep(1)
