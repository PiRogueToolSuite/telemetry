import hashlib
import json
import logging
import os
import platform
import uuid
from datetime import datetime
from enum import Enum
from platform import uname_result

import requests
from influxdb_client import Point, InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.write_api import SYNCHRONOUS


class TelemetryType(Enum):
    PIROGUE = {'measurement': 'pirogue', 'configuration_path': '/var/lib/pirogue/config',
               'bucket': 'telemetry', 'org': 'pts'}
    COLANDER = {'measurement': 'colander', 'configuration_path': '/var/lib/colander/config',
                'bucket': 'telemetry', 'org': 'pts'}
    UNKNOWN = {'measurement': 'unknown', 'configuration_path': '',
               'bucket': 'telemetry', 'org': 'pts'}

    def __getattribute__(self, name):
        value_dict = super().__getattribute__('_value_')
        if name in value_dict:
            return value_dict.get(name, None)
        else:
            return super().__getattribute__(name)

    @classmethod
    def get_type(cls, name):
        if name.lower() == 'pirogue':
            return TelemetryType.PIROGUE
        elif name.lower() == 'colander':
            return TelemetryType.COLANDER
        else:
            return TelemetryType.UNKNOWN


class TelemetryConfiguration:
    default_configuration_file_name: str = 'telemetry.json'
    configuration_file_path: str = ''

    def __init__(self, telemetry_type=TelemetryType.PIROGUE):
        self.unique_id: str = str(uuid.uuid4())
        self.enabled: bool = True
        self.host: str = ''
        self.port: int = 8086
        self.type: TelemetryType = telemetry_type
        self.token: str = ''
        self.ip_resolver_url: str = ''
        self.configuration_file_path = f'{self.type.configuration_path}/{self.default_configuration_file_name}'
        self.load_or_initialize()

    def load_or_initialize(self):
        if not os.path.isfile(self.configuration_file_path):
            raise Exception('Unable to load the configuration')
        with open(self.configuration_file_path, 'r') as config_file:
            config = json.load(config_file)
        unique_id = config.get('unique_id', None)
        self.load_from_dict(config)
        if not unique_id:
            self.save(force=True)

    def is_enabled(self):
        return self.enabled and self.token

    def as_json(self):
        return json.dumps(vars(self), indent=2, sort_keys=True, default=lambda x: x.name if isinstance(x, Enum) else x)

    def save(self, force=False):
        if os.path.isfile(self.configuration_file_path) and not force:
            print('La ?')
            return
        try:
            os.makedirs(self.type.configuration_path, exist_ok=True)
        except OSError:
            pass
        try:
            with open(self.configuration_file_path, mode='w') as config_file:
                json.dump(self.__dict__, config_file, indent=2, sort_keys=True,
                          default=lambda x: x.name if isinstance(x, Enum) else x)
        except Exception as e:
            raise Exception(f'Unable to save the default configuration {self.configuration_file_path}: {e}')

    def load_from_file(self):
        if not os.path.isfile(self.configuration_file_path):
            raise Exception(f'The telemetry configuration file {self.configuration_file_path} does not exist')
        with open(self.configuration_file_path, 'r') as config_file:
            config = json.load(config_file)
        self.load_from_dict(config)

    def load_from_dict(self, config: dict, prefix=''):
        enabled = bool(config.get(f'{prefix}enabled', self.enabled))
        self.enabled = enabled
        if not enabled:
            return self
        if not config.get(f'{prefix}unique_id', self.unique_id):
            raise Exception(f'The telemetry is not properly configured, parameter unique ID not set')
        self.unique_id = config.get(f'{prefix}unique_id', self.unique_id)
        self.host = config.get(f'{prefix}host', self.host)
        self.port = config.get(f'{prefix}port', self.port)
        self.type = TelemetryType.get_type(config.get(f'{prefix}type', self.type.name))
        self.token = config.get(f'{prefix}token', self.token)
        self.ip_resolver_url = config.get(f'{prefix}ip_resolver_url', self.ip_resolver_url)
        return self


class Telemetry:

    def __init__(self, configuration: TelemetryConfiguration):
        self.configuration: TelemetryConfiguration = configuration
        self.device_info: dict = {}

    def collect_data(self):
        if not self.configuration or not self.configuration.is_enabled():
            return None

        # Get device's public IP information
        unique_id = self.configuration.unique_id
        hashed_id = hashlib.sha256(unique_id.encode('UTF-8'))
        self.device_info: dict = {
            'unique_id': hashed_id.hexdigest()
        }
        try:
            response = requests.get(self.configuration.ip_resolver_url)
            if response.status_code == 200:
                ip_info = response.json()
                self.device_info['country_code'] = ip_info.get('country_code', 'unknown')
                self.device_info['country_name'] = ip_info.get('country_name', 'unknown')
                self.device_info['asn'] = ip_info.get('asn', 'unknown')
                self.device_info['asn_name'] = ip_info.get('as_desc', 'unknown')
        except Exception:
            self.device_info = {}
            return None

        # Get device information
        try:
            os_release: dict = platform.freedesktop_os_release()
            self.device_info['os_id'] = os_release.get('ID', 'unknown').lower()
            self.device_info['os_name'] = os_release.get('NAME', 'unknown').lower()
            self.device_info['os_version'] = os_release.get('VERSION_ID', 'unknown')
            system_info: uname_result = platform.uname()
            self.device_info['os_type'] = system_info.system.lower()
            self.device_info['os_arch'] = system_info.machine.lower()
        except Exception:
            self.device_info = {}
            return None

        return self.device_info

    def send_data(self):
        if not self.configuration or not self.configuration.is_enabled() or not self.device_info:
            return

        p = Point(self.configuration.type.measurement).time(datetime.utcnow().isoformat())
        for k, v in self.device_info.items():
            p.tag(k, v)
        p.field('value', 1)

        with InfluxDBClient(
                url=f'https://{self.configuration.host}:{self.configuration.port}',
                token=self.configuration.token,
                org=self.configuration.type.org
        ) as client:
            for _, logger in client.conf.loggers.items():
                logger.setLevel(logging.FATAL)
                logger.addHandler(logging.NullHandler())
            with client.write_api(write_options=SYNCHRONOUS) as write_api:
                try:
                    write_api.write(self.configuration.type.bucket, record=p)
                    write_api.close()
                except InfluxDBError as e:
                    raise Exception(f'An error occurred while sending the telemetry: {e}')


if __name__ == '__main__':
    pass
    # c = TelemetryConfiguration.get_default('ddf', TelemetryType.PIROGUE)
    # c = TelemetryConfiguration.load_from_file('/home/esther/Gre/projects/pts/pts-telemetry/trash/conf.json')
    # c = TelemetryConfiguration.load_from_environment()
    # print(c.as_json())
    # c.save(configuration_path='/home/esther/Gre/projects/pts/pts-telemetry/trash/', force=False)
    # t = Telemetry(c)
    # t.collect_data()
    # t.send_data()
    # print(json.dumps(t.device_info, indent=2, sort_keys=True))
