from disinfection_plc import DisinfectionPLC
from parameter import Parameter
from gadget import Gadget
from threading import Thread

from FloatModbusServer import FloatModbusServer
from time import sleep

water_level = Parameter(20.00, 45.00, 85.00, 0, 105.0, 5)
temperature = Parameter(19.0, 12.0, 26.0, 8.0, 3.0, 10)
dis_plc = DisinfectionPLC(water_level, temperature, 100)

def dis_plc_switch():
    running = server.data_bank.get_holding_registers(12)[0]
    take_in_valve = server.data_bank.get_holding_registers(13)[0]
    take_out_valve = server.data_bank.get_holding_registers(14)[0]
    automatic = server.data_bank.get_holding_registers(15)[0]
    concentration = server.read_float(16)
    chlorine = server.read_float(18)

    while True:
        current_running = server.data_bank.get_holding_registers(12)[0]
        current_take_in_valve = server.data_bank.get_holding_registers(13)[0]
        current_take_out_valve = server.data_bank.get_holding_registers(14)[0]
        current_automatic = server.data_bank.get_holding_registers(15)[0]
        current_concentration = server.read_float(16)
        current_chlorine = server.read_float(18)

        if concentration != current_concentration:
            concentration = current_concentration
            dis_plc.set_expected_concentration(concentration)

        if chlorine != current_chlorine:
            chlorine = current_chlorine
            dis_plc.set_chlorine(chlorine)

        if running != current_running:
            running = current_running
            dis_plc.switch_on_off()

        if take_in_valve != current_take_in_valve:
            take_in_valve = current_take_in_valve
            dis_plc.switch_intake_valve()

        if take_out_valve != current_take_out_valve:
            take_out_valve = current_take_out_valve
            dis_plc.switch_outlet_valve()

        if automatic != current_automatic:
            automatic = current_automatic
            dis_plc.switch_automatic()



if __name__ == '__main__':
    server = FloatModbusServer("127.0.0.1", 12346, no_block=True)
    server.start()
    # whole disinfection process is running
    server.data_bank.set_holding_registers(12, [1])
    # take in valve running
    server.data_bank.set_holding_registers(13, [1])
    # take out valve running
    server.data_bank.set_holding_registers(14, [1])
    # is automatic
    server.data_bank.set_holding_registers(15, [1])
    # default concentration
    server.write_float(16, 0.8)
    # default chlorine
    server.write_float(18, dis_plc.get_water_level())

    server.write_float(99, 60)

    switch_thread = Thread(target=dis_plc_switch, daemon=True)
    switch_thread.start()

    while True:
        dis_plc.dynamic_change()
        value_list = [dis_plc.get_water_level(),
                      dis_plc.get_temperature(),
                      dis_plc.get_chlorine(),
                      dis_plc.get_expected_concentration(),
                      dis_plc.get_real_concentration(),
                      dis_plc.get_ph()
                      ]

        server.write_floats(0, value_list)

        value_list.append(dis_plc.is_running)
        value_list.append(dis_plc.intake)
        value_list.append(dis_plc.outlet)
        value_list.append(dis_plc.is_automatic)

        water_level_last_tank = server.read_float(99)
        dis_plc.set_water_level_last_tank(water_level_last_tank)

        print(value_list)
        sleep(1)
