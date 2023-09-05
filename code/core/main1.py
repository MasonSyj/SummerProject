from parameter import Parameter
from gadget import Gadget
from threading import Thread
from raw_water_plc import raw_water_plc

from FloatModbusServer import FloatModbusServer
from time import sleep


def get_basic_plc_parameters():
    water_level = Parameter(70.00, 0, 150, 0, 150.0, 5)
    temperature = Parameter(17.0, 12.0, 26.0, 8.0, 3.0, 10)

    return water_level, temperature


water_level, temperature = get_basic_plc_parameters()

turbidity = Parameter(0.6, 0.3, 1.25, 0.0, 200.0, 1)
dissolved_solids = Parameter(150, 0, 550.0, 0, 10000, 30)
graverl_filter = Gadget(70, 2000)
sand_filter = Gadget(40, 1000)

rw_plc = raw_water_plc(water_level, temperature, 3)


def raw_water_plc_switch():
    pump_in_speed = server.data_bank.get_holding_registers(4)[0]
    flow_in_valve = server.data_bank.get_holding_registers(5)[0]
    flow_out_valve = server.data_bank.get_holding_registers(6)[0]
    running = server.data_bank.get_holding_registers(7)[0]

    while True:
        current_pump_in_speed = server.data_bank.get_holding_registers(4)[0]
        current_flow_in_valve = server.data_bank.get_holding_registers(5)[0]
        current_flow_out_valve = server.data_bank.get_holding_registers(6)[0]
        current_running = server.data_bank.get_holding_registers(7)[0]

        if current_flow_in_valve != flow_in_valve:
            flow_in_valve = current_flow_in_valve
            rw_plc.switch_intake_valve()

        if current_flow_out_valve != flow_out_valve:
            flow_out_valve = current_flow_out_valve
            rw_plc.switch_outlet_valve()

        if current_pump_in_speed != pump_in_speed:
            pump_in_speed = current_pump_in_speed
            rw_plc.set_pump_in_speed(pump_in_speed)

        if current_running != running:
            running = current_running
            rw_plc.switch_on_off()


if __name__ == '__main__':
    server = FloatModbusServer("127.0.0.1", 12344, no_block=True)
    server.start()

    # pump_in_speed, range: 0 - 10
    server.data_bank.set_holding_registers(4, [3])
    # take in valve running
    server.data_bank.set_holding_registers(5, [1])
    # take out valve running
    server.data_bank.set_holding_registers(6, [1])
    # main running
    server.data_bank.set_holding_registers(7, [1])

    switch_thread = Thread(target=raw_water_plc_switch, daemon=True)
    switch_thread.start()

    while True:
        rw_plc.dynamic_change()

        value_list = [rw_plc.get_water_level(),
                      rw_plc.get_temperature(),
                      ]

        server.write_floats(0, value_list)
        value_list.append(rw_plc.get_pump_in_speed())
        value_list.append(rw_plc.is_running)
        value_list.append(rw_plc.intake)
        value_list.append(rw_plc.outlet)
        print(value_list)

        sleep(1)
