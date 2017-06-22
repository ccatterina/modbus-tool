import attr
from pymodbus.constants import Defaults
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.transaction import ModbusRtuFramer, ModbusSocketFramer

@attr.s
class ModbusCore(object):
    ip = attr.ib()
    reg = attr.ib()
    reg_num = attr.ib()
    fcode = attr.ib(default=3)
    unit = attr.ib(default=None)
    framer = attr.ib(default='tcp')
    port = attr.ib(default=502)
    timeout = attr.ib(default=2)
    retries = attr.ib(default=2)

    MODBUS_FUNCTIONS = {
        1: ModbusTcpClient.read_coils,
        2: ModbusTcpClient.read_discrete_inputs,
        3: ModbusTcpClient.read_holding_registers,
        4: ModbusTcpClient.read_input_registers,
    }

    def __attrs_post_init__(self):
        Defaults.Timeout = self.timeout
        Defaults.Retries = self.retries
        framer = ModbusSocketFramer if self.framer == 'tcp' else ModbusRtuFramer
        self.client = ModbusTcpClient(host=self.ip, port=self.port, framer=framer)
        self.function = self.MODBUS_FUNCTIONS[self.fcode]

    def read(self, unit=None):
        if self.client.connect():
            data = self.function(self.client, self.reg, self.reg_num, unit=unit or self.unit)
            if data:
                try:
                    data = data.registers
                except Exception:
                    pass
            self.client.close()
        else:
            raise ConnectionError('Connection Failed')

        return data
