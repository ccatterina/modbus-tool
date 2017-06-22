#!/usr/bin/python
from __future__ import absolute_import

import time
import sys
import argparse
import logging

from core import ModbusCore

logger = logging.getLogger('modbus_tester')

parser = argparse.ArgumentParser(prog='modbus_tester.py',
                                 usage='%(prog)s ip reg reg_num [optional_args]')
parser.add_argument('ip', help='IP address or hostname of the device')
parser.add_argument('reg', help='Modbus Register index', type=int)
parser.add_argument('reg_num', help='Number of register to read', type=int)
parser.add_argument('-f', '--function', dest='fcode', default=3, type=int,
                    help='Modbus function code (default=3, available: 1, 2, 3, 4)')
parser.add_argument('-u', '--unit', dest='unit', default=None,
                    help='Unit id to test (Defualt=tests unit id from 1 to 254)', type=int)
parser.add_argument('-p', '--port', dest='port', default=502,
                    help='TCP port (Default=502)', type=int)
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
    logger.info("Try to reading reg %s at %s:%s with unit_id %s"
                % (args.reg, args.ip, args.port, args.unit if args.unit else "[1..254]"))
elif args.reg_num > 1:
    regs = "[%s..%s]" % (args.reg, args.reg + args.reg_num - 1)
    logger.info("Try to reading regs %s at %s:%s with unit_id %s"
                % (regs, args.ip, args.port, args.unit if args.unit else "[1..254]"))
else:
    logger.error("reg_num must be a positive non-zero integer")
    sys.exit(1)

modbus = ModbusCore(args.ip, args.reg, args.reg_num, args.fcode,
                    args.unit, args.framer, args.port, args.timeout, args.retries)
if not args.unit:
    for x in range(1, 255):
        logger.info("Reading unit %s" % x)
        logger.info(modbus.read(x))
else:
    logger.info(modbus.read())
