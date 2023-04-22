import time
from enum import Enum

import psutil
from urllib import request
import requests


def get_process_info(process_name) -> dict:
    """
    Returns a dictionary with information about the process with the given name.
    :param process_name: name of the process to get information about
    :return: dictionary with information about the process
    """
    for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info']):
        if proc.info['name'] == process_name:
            return {
                'name': proc.info['name'],
                'cpu_percent': proc.info['cpu_percent']*100,
                'memory_rss': proc.info['memory_info'].rss,
            }


def get_service_info(service_list) -> dict:
    """
    Returns a dictionary with information about the processes associated with the given services.
    :param service_list: list of services to get information about
    :return: dictionary with information about the services
    """
    service_info = {}
    for service in service_list:
        process_info = get_process_info(service)
        if process_info:
            service_info[service] = process_info
    return service_info


def is_network_working(host_check='https://google.com') -> bool:
    """
    Returns a dictionary with information about the network status.
    :param host_check: host to ping
    :return: True if the host is reachable, False otherwise
    """
    try:
        request.urlopen(host_check, timeout=1)
        return True
    except:
        return False


SLEEP_TIME = 30  # seconds
PROCESS_LIST = ['msedge.exe', 'pycharm64.exe', 'python.exe']
IP_LOCAL_CHECK = "http://192.168.1.1"


def send_data_to_device(data) -> bool:
    """
    Sends the given data to the FiPy device using serial communication.
    :param data: data to send to FiPy device
    :return: True if the data was sent successfully, False otherwise
    """
    # TODO: this method should be tried 3 times before giving up
    raise NotImplementedError


def send_data_to_api(data) -> bool:
    """
    Sends the given data to the API using the normal network.
    :param data: data to send to the API
    :return: True if the data was sent successfully, False otherwise
    """
    url = 'http://localhost/monitor/data'

    response = requests.post(url, json=data)

    if response.status_code == 200 and response.reason == 'OK':
        return True
    else:
        print(f'Error al hacer la petición: {response.status_code} - {response.reason}')
        return False


def wait_for_communication():
    """
    Waits until the program receives an instruction from the device
    :return: 1 if the device expects to retrieve data, 2 if data should be sent to the API, 3 to check internet connection and the eui
    """
    #TODO: still to be implemented along with the serial communication
    #TODO: receive the option from the serial communication
    #TODO: RECEIVE THE eui from the serial communication
    return 2, "123456789"


class Option(Enum):
    SEND_TO_DEVICE = 1
    SEND_TO_API = 2
    CHECK_INTERNET_CONNECTION = 3


def main():
    try:
        while True:
            option, device_eui = wait_for_communication()

            if option == Option.SEND_TO_DEVICE or option == Option.SEND_TO_API:

                services_information = get_service_info(PROCESS_LIST)
                system_load_average = psutil.getloadavg()[0] * 100
                disk_usage = psutil.disk_usage('/').percent
                memory_usage = psutil.virtual_memory().percent
                wan_access = is_network_working()
                lan_access = is_network_working(IP_LOCAL_CHECK)

                data = {"services": services_information,
                        "load_avg": system_load_average,
                        "disk": disk_usage,
                        "mem": memory_usage,
                        "wan": wan_access,
                        "lan": lan_access,
                        "eui": device_eui}

                print("Services info:\n", services_information)
                print("System load average: {}".format(system_load_average))
                print("Disk usage: {}".format(disk_usage))
                print("Memory usage: {}".format(memory_usage))

                print("WAN access: {}".format(("OK" if wan_access else "Not OK")))
                print("LAN access: {}".format(("OK" if lan_access else "Not OK")))

                if option == Option.SEND_TO_DEVICE:
                    print("No internet connection, transmitting info to device...")
                    send_data_to_device(data)
                else:
                    print("Internet connection available, transmitting info to API...")
                    send_data_to_api(data)

            elif option == Option.CHECK_INTERNET_CONNECTION:
                print("Checking internet connection...")

                wan_access = is_network_working()
                lan_access = is_network_working(IP_LOCAL_CHECK)

                send_data_to_device((wan_access, lan_access))

    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == '__main__':
    main()
