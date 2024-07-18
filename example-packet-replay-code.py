import logging

import psutil
from cyberx import process
from cyberx.config import ConfigurationWrapper
from cyberx.web.django_helpers import UserFriendlyException

logger = logging.getLogger(__name__)


def _get_active_monitor_interface_name():
    config = ConfigurationWrapper('network')
    monitor_interfaces = config.get('monitor_interfaces').split(',')
    activate_interfaces = {ifname for ifname,
                           info in psutil.net_if_stats().items() if info.isup}
    return next((ifname for ifname in monitor_interfaces if ifname in activate_interfaces), None)


def run_tcpreplay(pcap_path, extra_params=None):
    logger.info(f"runnning pcap {pcap_path}")
    active_monitor_interface = _get_active_monitor_interface_name()
    if not active_monitor_interface:
        logger.error('no active monitoring interface')
        raise UserFriendlyException('No monitoring interface')
    logger.info(f"interface: {active_monitor_interface}")

    command = ['sudo', 'tcpreplay', '-i', active_monitor_interface]
    if extra_params:
        command.extend(extra_params)
    command.append(pcap_path)

    logger.info(f"running: {' '.join(command)}")
    process.run(command, raise_on_failure=True)
