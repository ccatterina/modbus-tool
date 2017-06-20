#!/usr/bin/python
import time
import sys
import argparse
import logging

from pymodbus.constants import Defaults
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.transaction import ModbusRtuFramer, ModbusSocketFramer

logger = logging.getLogger('modbus_tester')

parser = argparse.ArgumentParser(prog='modbus_tester.py', usage='%(prog)s ip reg reg_num [optional_args]')
parser.add_argument('ip', help='IP address or hostname of the device')
parser.add_argument('reg', help='Modbus Register index', type=int)
parser.add_argument('reg_num', help='Number of register to read', type=int)
parser.add_argument('-u', '--unit', dest='unit', default=None,
                    help='Unit id to test (Defualt=tests unit id from 1 to 254)', type=int)
parser.add_argument('-p', '--port', dest='port', default=502, help='TCP port (Default=502)', type=int)
parser.add_argument('-t', '--timeout', dest='timeout', default=2,
                    help='Timeout in seconds.(default=2)', type=int)
parser.add_argument('-n', '--retries', dest='retries', default=2,
                    help='Number of retries. (default=2)', type=int)
parser.add_argument('-r', '--rtu', dest='framer', default='tcp', action='store_const',
                    const='rtu', help='Rtu over TCP (default: ModbusTCP)')
parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_const',
                    const=True, help='Verbose mode, print debug information.')

args = parser.parse_args()
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('modbus_tester')

if args.reg < 0:
    logger.info("reg must be a positive integer")
    sys.exit(1)

if args.reg_num == 1:
    logger.info("Testing reg %s at ip %s with unit_id %s"
                % (args.reg, args.ip, args.unit if args.unit else "[1..254]"))
elif args.reg_num > 1:
    regs = "[%s..%s]" % (args.reg, args.reg + args.reg_num - 1)
    logger.info("Testing regs %s at ip %s with unit_id %s"
                % (regs, args.ip, args.unit if args.unit else "[1..254]"))
else:
    logger.error("reg_num must be a positive non-zero integer")
    sys.exit(1)

Defaults.Timeout = args.timeout
Defaults.Retries = args.retries
framer = ModbusSocketFramer if args.framer == 'tcp' else ModbusRtuFramer
client = ModbusTcpClient(host=args.ip, port=args.port, framer=framer)

if not args.unit:
    for x in range(1, 255):
        if client.connect():
            logger.info("Testing unit %s" % x)
            data = client.read_holding_registers(args.reg, args.reg_num, unit=x)
            if data:
                try:
                    logger.info('Result -> %s', data.registers)
                except Exception:
                    logger.info('Result -> %s', data)
            else:
                logger.info('No reply from the device')
            client.close()
    else:
        logger.error('Failed to connect')
        sys.exit(1)
else:
    if client.connect():
        data = client.read_holding_registers(args.reg, args.reg_num, unit=args.unit)
        if data:
            try:
                logger.info('Result -> %s', data.registers)
            except Exception:
                logger.info('Result -> %s', data)
        else:
            logger.info('No reply from the device')
        client.close()
    else:
        logger.error('Failed to connect')
        sys.exit(1)
