from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import encode_ieee, decode_ieee, long_list_to_word, word_list_to_long
from pyModbusTCP.server import ModbusServer


class FloatModbusClient(ModbusClient):
    def read_float(self, address, number=2):
        num_32b_list = self.read_holding_registers(address, number)
        if num_32b_list is None:
            print("fail to read")
            return
        else:
            float_num_32b_msb, float_num_32b_lsb = num_32b_list
        float_num_32b = word_list_to_long([float_num_32b_msb, float_num_32b_lsb])[0]
        flat_num = decode_ieee(float_num_32b)
        return flat_num

    def write_float(self, address, float_num):
        float_num_32b = encode_ieee(float_num)
        # following function only accept a list of integers, cannot be a single integer
        float_num_32b_msb, float_num_32b_lsb = long_list_to_word([float_num_32b])
        self.write_single_register(address, float_num_32b_msb)
        self.write_single_register(address + 1, float_num_32b_lsb)

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
    c.write_float(0, 12.25)
    float_num = c.read_float(0)
    assert float_num == 12.25

def test_multiple_floats():
    nums_list = [12.25, 33.34, 12.01, 10.13, 99.13]
    c.write_floats(0, nums_list)

    returned_nums_list = c.read_floats(0, len(nums_list))

    for i in range(len(nums_list)):
        assert nums_list[i] == returned_nums_list[i]

    print(returned_nums_list)


if __name__ == '__main__':
    server = ModbusServer(port=12345, no_block=True)
    server.start()
    c = FloatModbusClient(host='127.0.0.1', port=12345, auto_open=True)

    test_single_float()
    test_multiple_floats()

    c.close()
    server.stop()
