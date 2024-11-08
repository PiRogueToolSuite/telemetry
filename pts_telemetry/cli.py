import sys
import argparse
import logging
import pprint

from pts_telemetry.telemetry import TelemetryConfiguration, Telemetry

LOG_FORMAT = '[%(name)s] %(message)s'
logging.basicConfig(level='INFO', format=LOG_FORMAT)
logger = logging.getLogger('pirogue_telemetry')


def __show_telemetry_configuration():
    configuration = TelemetryConfiguration(auto_load=True)
    print(configuration.as_json())


def __initialize_telemetry_configuration():
    configuration = TelemetryConfiguration(auto_load=True)
    configuration.save(force=True)


def __disable_telemetry():
    configuration = TelemetryConfiguration(auto_load=True)
    configuration.enabled = False
    configuration.save(force=True)
    logger.info('PiRogue telemetry is now disabled')


def __collect_telemetry():
    configuration = TelemetryConfiguration(auto_load=True)
    logger.info('Collecting PiRogue telemetry')
    telemetry = Telemetry(configuration)
    telemetry.collect_data()
    telemetry.send_data()


def __display_telemetry():
    configuration = TelemetryConfiguration(auto_load=True)
    logger.info('Displaying PiRogue telemetry')
    telemetry = Telemetry(configuration)
    telemetry.collect_data()
    # This doesn't use an InfluxDB connection contrary to send_data():
    pprint.pprint(telemetry.device_info)


def main():
    arg_parser = argparse.ArgumentParser(prog='telemetry', description='PiRogue telemetry CLI')
    subparsers = arg_parser.add_subparsers(dest='func')
    # Configuration
    config_group = subparsers.add_parser('config', help='Manage telemetry configuration')
    config_group.add_argument('action', type=str, help='Initialize, show or disable telemetry configuration',
                              nargs='?',
                              choices=['init', 'show', 'disable'])
    # Collection
    subparsers.add_parser('collect', help='Collect and send telemetry data')
    subparsers.add_parser('display', help='Collect and display telemetry data')

    args = arg_parser.parse_args()
    if not args.func:
        arg_parser.print_help()
        return

    if args.func == 'config':
        if args.action == 'init':
            try:
                __initialize_telemetry_configuration()
            except Exception as e:
                logger.error(e)
                sys.exit(1)
        elif args.action == 'show':
            try:
                __show_telemetry_configuration()
            except Exception as e:
                logger.error(e)
                sys.exit(1)
        elif args.action == 'disable':
            try:
                __disable_telemetry()
            except Exception as e:
                logger.error(e)
                sys.exit(1)
    elif args.func == 'collect':
        try:
            __collect_telemetry()
        except Exception as e:
            logger.error(e)
            sys.exit(1)
    elif args.func == 'display':
        try:
            __display_telemetry()
        except Exception as e:
            logger.error(e)
            sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
