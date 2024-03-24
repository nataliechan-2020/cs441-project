import logging
import datetime
import re
from termcolor import colored
import os

def create_logfile():
    if not os.path.exists("log_file.txt"):
       f = open("log_file.txt", "w")
        
def configure_log():
    logging.basicConfig(filename="log_file.txt", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def logs_details(type, msg):
    # use warning, info
    configure_log()

    if (type=="warning"):
        logging.warning(msg)
    else:
        logging.info(msg)


def alert(msg):
    print (colored('ALERT: '+ msg, 'red'))
    logs_details("warning", msg)

def info(msg):
    logs_details("info", msg)

def clear_log():
    current_date = datetime.datetime.now()
    threshold = current_date - datetime.timedelta(days=5)

    pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"

    
    with open ("log_file.txt", 'r') as file:
        logs = file.readline()
        
    for log in logs:
        match = re.search(pattern,log)
        if match:
            str = match.group(0)
            timestamp = datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S')

            if timestamp<threshold:
                log.remove()
    with open("log_file.txt", "w") as file:
        file.writelines(logs)

# IP Spoofing Logs
def flag_ip_spoofing(sorc_ip, dest_ip):
    alert_msg = "IP Spoofing Detected; Source IP: {sorc_ip}, Destionation IP: {dest_ip}" .format(sorc_ip=sorc_ip, dest_ip=dest_ip)
    alert(alert_msg)

def log(sorc_ip, dest_ip, data):
    msg = "Source IP: {sorc_ip}, Destionation IP: {dest_ip}, Data: {data} " .format(sorc_ip=sorc_ip, dest_ip=dest_ip, data=data)
    info(msg)



# Firewall Logs
    

# Packet Sniffing Logs


