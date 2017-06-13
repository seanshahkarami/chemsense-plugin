#!/usr/bin/env python3
import waggle.pipeline
import logging
from serial import Serial
import os
import re


logging.basicConfig(level=logging.INFO)
device = os.environ.get('CHEMSENSE_DEVICE', '/dev/tty.usbserial-142A')


class ChemsensePlugin(waggle.pipeline.Plugin):

    logger = logging.getLogger('ChemsensePlugin')

    plugin_name = 'chemsense'
    plugin_version = '1'

    def run(self):
        with Serial(device, baudrate=115200, timeout=1) as s:
            data = {}

            while True:
                try:
                    line = s.readline().decode()
                except UnicodeDecodeError:
                    continue

                self.logger.debug('line: {}'.format(line))

                if len(line) == 0:
                    if data:
                        del data['SQN']

                        agg = ' '.join('{}={}'.format(k, v) for k, v in data.items())
                        self.send('agg', agg)
                    data = {}
                    continue

                if re.search('SQN=', line):
                    data.update(dict(re.findall('(\S+)=(\S+)', line)))
                    continue


if __name__ == '__main__':
    plugin = ChemsensePlugin.defaultConfig()
    plugin.run()
