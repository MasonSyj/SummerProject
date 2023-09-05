from pyModbusTCP.utils import encode_ieee, decode_ieee, long_list_to_word, word_list_to_long
from pyModbusTCP.server import ModbusServer


class FloatModbusServer(ModbusServer):
    def read_float(self, address, number=2):
        float_num_32b_msb, float_num_32b_lsb = self.data_bank.get_holding_registers(address, number)
        float_num_32b = word_list_to_long([float_num_32b_msb, float_num_32b_lsb])[0]
        flat_num = decode_ieee(float_num_32b)
        return flat_num

    def write_float(self, address, float_num):
        float_num_32b = encode_ieee(float_num)
        # following function only accept a list of integers, cannot be a single integer
        float_num_32b_msb, float_num_32b_lsb = long_list_to_word([float_num_32b])
        self.data_bank.set_holding_registers(address, [float_num_32b_msb, float_num_32b_lsb])

    def write_floats(self, address, float_list):
        size = len(float_list)
        for i in range(size):
            self.write_float(address + i * 2, float_list[i])

    def read_floats(self, address, size):
        floats_list = []
        for i in range(size):
            floats_list.append(round(self.read_float(address + i * 2) * 1000) / 1000)
        return floats_list


def test_single_float():
    float_num = 12.25
    server.write_float(0, float_num)
    assert float_num == server.read_float(0)


def test_multiple_floats():
    nums_list = [12.25, 33.34, 12.01, 10.13, 99.13]
    server.write_floats(0, nums_list)

    returned_nums_list = server.read_floats(0, len(nums_list))

    for i in range(len(nums_list)):
        assert nums_list[i] == returned_nums_list[i]

    print(returned_nums_list)



if __name__ == '__main__':
    server = FloatModbusServer(port=12345, no_block=True)
    server.start()

    test_multiple_floats()


    server.stop()
