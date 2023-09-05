from parameter import Parameter
from gadget import Gadget
from threading import Thread
from storage_plc import storage_plc

from FloatModbusServer import FloatModbusServer
from time import sleep


def get_basic_plc_parameters():
    water_level = Parameter(65.00, 50.00, 110.00, 0, 150.0, 5)
    temperature = Parameter(20.0, 12.0, 26.0, 8.0, 3.0, 10)

    return water_level, temperature


water_level, temperature = get_basic_plc_parameters()

turbidity = Parameter(0.6, 0.3, 1.25, 0.0, 200.0, 1)
dissolved_solids = Parameter(150, 0, 550.0, 0, 10000, 30)
graverl_filter = Gadget(70, 2000)
sand_filter = Gadget(40, 1000)

st_plc = storage_plc(water_level, temperature, 100, 77, 5)


def raw_water_plc_switch():
    pump_in_speed = server.data_bank.get_holding_registers(4)[0]
    flow_in_valve = server.data_bank.get_holding_registers(5)[0]
    flow_out_valve = server.data_bank.get_holding_registers(6)[0]
    automatic = server.data_bank.get_holding_registers(7)[0]
    running = server.data_bank.get_holding_registers(8)[0]

    while True:
        current_pump_in_speed = server.data_bank.get_holding_registers(4)[0]
        current_flow_in_valve = server.data_bank.get_holding_registers(5)[0]
        current_flow_out_valve = server.data_bank.get_holding_registers(6)[0]
        current_automatic = server.data_bank.get_holding_registers(7)[0]
        current_running = server.data_bank.get_holding_registers(8)[0]

        if current_flow_in_valve != flow_in_valve:
            flow_in_valve = current_flow_in_valve
            st_plc.switch_intake_valve()

        if current_flow_out_valve != flow_out_valve:
            flow_out_valve = current_flow_out_valve
            st_plc.switch_outlet_valve()

        if current_pump_in_speed != pump_in_speed:
            pump_in_speed = current_pump_in_speed
            st_plc.set_pump_out_speed(pump_in_speed)

        if current_automatic != automatic:
            automatic = current_automatic
            st_plc.switch_automatic()

        if current_running != running:
            running = current_running
            st_plc.switch_on_off()


if __name__ == '__main__':
    server = FloatModbusServer("127.0.0.1", 12347, no_block=True)
    server.start()

    # pump_in_speed, range: 0 - 10
    server.data_bank.set_holding_registers(4, [6])
    # take in valve running
    server.data_bank.set_holding_registers(5, [1])
    # take out valve running
    server.data_bank.set_holding_registers(6, [1])
    # is automatic
    server.data_bank.set_holding_registers(7, [1])
    # main running
    server.data_bank.set_holding_registers(8, [1])

    # origin water level in the previous tank, needs to be set beforehand just in case
    server.write_float(99, 20)

    switch_thread = Thread(target=raw_water_plc_switch, daemon=True)
    switch_thread.start()

    while True:
        st_plc.dynamic_change()

        value_list = [st_plc.get_water_level(),
                      st_plc.get_temperature(),
                      ]

        server.write_floats(0, value_list)
        value_list.append(st_plc.get_pump_out_speed())
        value_list.append(st_plc.intake)
        value_list.append(st_plc.outlet)
        value_list.append(st_plc.is_automatic)
        value_list.append(st_plc.is_running)

        water_level_last_tank = server.read_float(99)
        st_plc.set_water_level_last_tank(water_level_last_tank)

        print(value_list)

        sleep(1)
