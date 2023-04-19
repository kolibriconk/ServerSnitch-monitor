import time
import psutil
from urllib import request


def get_process_info(process_name):
    """
    Returns a dictionary with information about the process with the given name.
    """
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        if proc.info['name'] == process_name:
            return {
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu_percent': proc.info['cpu_percent'],
                'memory_rss': proc.info['memory_info'].rss,
            }


def get_service_info(service_list):
    """
    Returns a dictionary with information about the processes associated with the given services.
    """
    service_info = {}
    for service in service_list:
        process_info = get_process_info(service)
        if process_info:
            service_info[service] = process_info
    return service_info


def is_network_working(host_check='https://google.com'):
    """
    Returns a dictionary with information about the network status.
    """
    try:
        request.urlopen(host_check, timeout=1)
        return True
    except:
        return False


RECHECK_TIME = 15
PROCESS_LIST = ['msedge.exe', 'pycharm64.exe', 'python.exe']

def main():
    try:
        while True:
            ip_local_check = "http://192.168.1.1"
            services_information = get_service_info(PROCESS_LIST)

            system_load_average = psutil.getloadavg()

            print("Services info:\n", services_information)
            print("System load average: {}".format(system_load_average[0] * 100))  # just for UNIX systems
            print("Disk usage: {}".format(psutil.disk_usage('/').percent))
            print("Memory usage: {}".format(psutil.virtual_memory().percent))

            print("WAN access: {}".format(("OK" if is_network_working() else "Not OK")))
            print("LAN access: {}".format(("OK" if is_network_working(ip_local_check) else "Not OK")))

            time.sleep(RECHECK_TIME)
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == '__main__':
    main()
