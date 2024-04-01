import requests
import os
import yaml
import time
import argparse
import sys
class Robot:
    def __init__(self, config):
        self.x = x
        self.y = y
        self.position = (self.x, self.y)
        self.item = item
        self.ip = config.get('device_ip_addr')
        self.url = f'{self.ip}/cgi-bin/param_setting.cgi'
        self.data = config
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Origin': 'http://192.168.1.222',
            'Connection': 'keep-alive',
            'Referer': 'http://192.168.1.222/cgi-bin/param_setting.cgi',
            'Upgrade-Insecure-Requests': '1'
        }

def load_yaml(lidar_file):
    config_file = os.path.join(lidar_file)
    f = open(lidar_file, 'r')
    config = yaml.safe_load(f)
    f.close
    return config
def configure_lidar(lidar_file, previous_ip):
    config_file = os.path.join(lidar_file)
    f = open(lidar_file, 'r')
    config = yaml.safe_load(f)
    f.close()
    lidar = RBLidar(config)
    current_ip = lidar.ip
    lidar.ip = previous_ip
    lidar_name = lidar_file.split('.')[0]

    print(f"Configuration for {lidar_name}:")
    # print(IP)
    # print("URL:", lidar.url)
    # print("Data:", lidar.data)
    print("\n")
    return current_ip

if __name__ == "__main__":
    lidar_list = [
        "robosense_top.yaml",
        "robosense_top_front.yaml",
        "robosense_left.yaml",
        "robosense_right.yaml",
        "rs_bp_left.yaml",
        "rs_M1_front.yaml",
        "rs_M1_left.yaml",
        "rs_M1_right.yaml",
        "rs_bp_right.yaml",
    ]

    for lidar_config in lidar_list:
        current_ip = configure_lidar(lidar_config, previous_ip)
        previous_ip = current_ip
        print(current_ip)
        print(previous_ip)


    print("Lidar configuration complete")