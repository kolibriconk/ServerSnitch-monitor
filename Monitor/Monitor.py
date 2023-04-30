from enum import IntEnum

import psutil
from urllib import request
import requests
import binascii
from serial import Serial


class Option(IntEnum):
    SEND_TO_DEVICE = 1
    SEND_TO_API = 2
    CHECK_INTERNET_CONNECTION = 3


class Monitor:

    def __init__(self, sleep_time=30, service_list=None, ip_local_check="http://192.168.1.1"):
        self.sleep_time = sleep_time
        self.service_list = service_list
        self.ip_local_check = ip_local_check
        self.serial = None

    def set_up_serial(self, port, baudrate=115200, timeout=5):
        """
        Sets up the serial communication with the FiPy device.
        """
        self.serial = Serial(port, baudrate, timeout=timeout)
        self.serial.close()

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def send_data_to_api(data) -> bool:
        """
        Sends the given data to the API using the normal network.
        :param data: data to send to the API
        :return: True if the data was sent successfully, False otherwise
        """
        try:
            url = 'http://localhost:5000/monitor/data'

            response = requests.post(url, json=data)

            if response.status_code == 200 and response.reason == 'OK':
                return True
            else:
                print(f'Error al hacer la petición: {response.status_code} - {response.reason}')
                return False
        except Exception as e:
            print(f'Error al hacer la petición: {e}')
            return False

    def get_service_info(self) -> dict:
        """
        Returns a dictionary with information about the processes associated with the given services.
        :param service_list: list of services to get information about
        :return: dictionary with information about the services
        """
        service_info = {}
        for service in self.service_list:
            process_info = self.get_process_info(service)
            if process_info:
                service_info[service] = process_info
        return service_info

    def send_data_to_device(self, data) -> bool:
        """
        Sends the given data to the FiPy device using serial communication.
        :param data: data to send to FiPy device
        :return: True if the data was sent successfully, False otherwise
        """
        self.serial.open()
        self.serial.write(data.encode())
        self.serial.close()

        return True

    def wait_for_command(self) -> (int, str):
        """
        Waits until the program receives an instruction from the device and the eui
        :return: 1 if the device expects to retrieve data, 2 if data should be sent to the API,
        3 to check internet connection
        """
        self.serial.open()
        loop = True
        command = eui = None
        while loop:
            message = self.serial.readline()
            if b"configsnitch" in message:
                message = message.decode("ascii")
                command = message.split("!")[1]
                eui = message.split("!")[2]
                loop = False

        self.serial.close()
        return int(command), eui

    def main(self):
        try:
            self.set_up_serial('COM5')
            while True:
                command, device_eui = self.wait_for_command()
                print(f"Option: {command} - EUI: {device_eui}")
                if command is None or device_eui is None:
                    print("Not getting command nor eui, trying again...")
                    continue
                if command == int(Option.SEND_TO_DEVICE) or command == int(Option.SEND_TO_API):
                    print("Getting system information...")
                    services_information = self.get_service_info()
                    system_load_average = psutil.getloadavg()[0] * 100
                    disk_usage = psutil.disk_usage('/').percent
                    memory_usage = psutil.virtual_memory().percent
                    wan_access = self.is_network_working()
                    lan_access = self.is_network_working(self.ip_local_check)

                    data = {"services": services_information,
                            "load_avg": system_load_average,
                            "disk": disk_usage,
                            "mem": memory_usage,
                            "wan": wan_access,
                            "lan": lan_access,
                            "eui": device_eui}

                    # print("Services info:\n", services_information)
                    # print("System load average: {}".format(system_load_average))
                    # print("Disk usage: {}".format(disk_usage))
                    # print("Memory usage: {}".format(memory_usage))
                    #
                    # print("WAN access: {}".format(("OK" if wan_access else "Not OK")))
                    # print("LAN access: {}".format(("OK" if lan_access else "Not OK")))

                    print(data)

                    if command == int(Option.SEND_TO_DEVICE):
                        print("No internet connection, transmitting info to device...")
                        # self.send_data_to_device(data)
                    else:
                        print("Internet connection available, transmitting info to API...")
                        self.send_data_to_api(data)

                elif command == int(Option.CHECK_INTERNET_CONNECTION):
                    print("Checking internet connection...")

                    wan_access = self.is_network_working()
                    lan_access = self.is_network_working(self.ip_local_check)

                    self.send_data_to_device(f"serverconnection!{wan_access}!{lan_access}")

        except KeyboardInterrupt:
            print("Exiting...")


if __name__ == '__main__':
    app = Monitor(sleep_time=30, service_list=['msedge.exe', 'pycharm64.exe', 'python.exe'])
    app.main()
