import time
import psutil
from urllib import request


def get_process_info(process_name) -> dict:
    """
    Returns a dictionary with information about the process with the given name.
    :param process_name: name of the process to get information about
    :return: dictionary with information about the process
    """
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        if proc.info['name'] == process_name:
            return {
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu_percent': proc.info['cpu_percent'],
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
    :return:
    """
    # TODO: this method should be tried 3 times before giving up, if not success send it via FiPy
    raise NotImplementedError


def main():
    try:
        while True:

            services_information = get_service_info(PROCESS_LIST)
            system_load_average = psutil.getloadavg()[0]*100
            disk_usage = psutil.disk_usage('/').percent
            memory_usage = psutil.virtual_memory().percent
            wan_access = is_network_working()
            lan_access = is_network_working(IP_LOCAL_CHECK)

            data = {services_information, system_load_average, disk_usage, memory_usage, wan_access, lan_access}

            print("Services info:\n", services_information)
            print("System load average: {}".format(system_load_average))
            print("Disk usage: {}".format(disk_usage))
            print("Memory usage: {}".format(memory_usage))

            print("WAN access: {}".format(("OK" if wan_access else "Not OK")))
            print("LAN access: {}".format(("OK" if lan_access else "Not OK")))

            if not wan_access:
                print("No internet connection, transmitting info to device...")
                send_data_to_device(data)
            if wan_access:
                print("Internet connection available, transmitting info to API...")
                send_data_to_api(data)

            time.sleep(SLEEP_TIME)
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == '__main__':
    main()
