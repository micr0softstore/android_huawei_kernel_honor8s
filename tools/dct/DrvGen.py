#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (C) 2016 MediaTek Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See http://www.gnu.org/licenses/gpl-2.0.html for more details.

import os
import sys
import getopt
import traceback
import subprocess
import xml.dom.minidom

sys.dont_write_bytecode = True

sys.path.append('.')
sys.path.append('..')

# Import chip definitions and utilities
from obj.ChipObj import (
    ChipObj,
    Everest,
    Olympus,
    MT6757_P25,
    Rushmore,
    Whitney,
    MT6759,
    MT6763,
    MT6750S,
    MT6758,
    MT6739,
    MT8695,
    MT6771,
    MT6775,
    MT6779,
)

from utility.util import LogLevel, log


def usage():
    print('''
usage: DrvGen [dws_path] [file_path] [log_path] [paras]...

options and arguments:

dws_path    :    dws file path
file_path   :    where you want to put generated files
log_path    :    where to store the log files
paras       :    parameters for generating wanted file
''')


def is_oldDws(path, gen_spec):
    if not os.path.exists(path):
        log(LogLevel.error, f'Cannot find {path}')
        sys.exit(-1)

    try:
        xml.dom.minidom.parse(dws_path)
    except Exception as e:
        log(LogLevel.warn, f'{dws_path} is not XML format, trying to use old DCT!')
        if len(gen_spec) == 0:
            log(LogLevel.warn, 'Please use old DCT UI to generate all files!')
            return True
        old_dct = os.path.join(sys.path[0], 'old_dct', 'DrvGen')
        cmd = f'{old_dct} {dws_path} {gen_path} {log_path} {gen_spec[0]}'
        if subprocess.call(cmd, shell=True) == 0:
            return True
        else:
            log(LogLevel.error, f'{dws_path} format error!')
            sys.exit(-1)

    return False


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], '')

    if len(args) == 0:
        msg = 'Too few arguments!'
        usage()
        log(LogLevel.error, msg)
        sys.exit(-1)

    dws_path = ''
    gen_path = ''
    log_path = ''
    gen_spec = []

    # Parse arguments
    dws_path = os.path.abspath(args[0])

    if len(args) == 1:
        gen_path = os.path.dirname(dws_path)
        log_path = os.path.dirname(dws_path)
    elif len(args) == 2:
        gen_path = os.path.abspath(args[1])
        log_path = os.path.dirname(dws_path)
    elif len(args) == 3:
        gen_path = os.path.abspath(args[1])
        log_path = os.path.abspath(args[2])
    elif len(args) >= 4:
        gen_path = os.path.abspath(args[1])
        log_path = os.path.abspath(args[2])
        gen_spec = args[3:]

    log(LogLevel.info, f'DWS file path is {dws_path}')
    log(LogLevel.info, f'Gen files path is {gen_path}')
    log(LogLevel.info, f'Log files path is {log_path}')
    for item in gen_spec:
        log(LogLevel.info, f'Parameter is {item}')

    # Validate paths
    for path in (dws_path, gen_path, log_path):
        if not os.path.exists(path):
            log(LogLevel.error, f'Cannot find "{path}", path does not exist!')
            sys.exit(-1)

    if is_oldDws(dws_path, gen_spec):
        sys.exit(0)

    chipId = ChipObj.get_chipId(dws_path)
    log(LogLevel.info, f'chip id: {chipId}')

    chip_map = {
        'MT6797': Everest,
        'MT6757': Olympus,
        'MT6757-P25': MT6757_P25,
        'KIBOPLUS': MT6757_P25,
        'MT6570': Rushmore,
        'MT6799': Whitney,
        'MT6763': MT6763,
        'MT6759': MT6759,
        'MT6750S': MT6750S,
        'MT6758': MT6758,
        'MT6739': MT6739,
        'MT8695': MT8695,
        'MT6771': MT6771,
        'MT6775': MT6771,
        'MT6765': MT6771,
        'MT3967': MT6771,
        'MT6761': MT6771,
        'MT6779': MT6779,
    }

    chip_class = chip_map.get(chipId, ChipObj)
    chipObj = chip_class(dws_path, gen_path)

    if not chipObj.parse():
        log(LogLevel.error, f'Parse {dws_path} failed!')
        sys.exit(-1)

    if not chipObj.generate(gen_spec):
        log(LogLevel.error, 'Generate files failed!')
        sys.exit(-1)

    sys.exit(0)
