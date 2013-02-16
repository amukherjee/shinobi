#!/usr/local/bin/python2.7
import sys
import io
import signal
import os
import subprocess
from socket import gethostname
from ConfigParser import RawConfigParser

def access_instance_setup(filename):
    """Spools in the database settings described in configuration file."""
    
    config = RawConfigParser(allow_no_value=True)
    config.readfp(open(filename))

    socket = []
    port = []
    running_process =[]
    un_important=[]

    un_important=['mysqld_multi',
                  'client',
                  'mysqldump',
                  'mysql',
                  'isamchk',
                  'myisamchk',
                  'mysqlhotcopy'] 

    for section_name in config.sections():
        if section_name in un_important:
            pass
        else:
            socket = config.get(section_name,'socket')
            port = config.get(section_name,'port')

            process_specs = port
            server_status = check_server_status(port)
            
            if server_status == '\t\tRUNNING':
                replication_vars = check_replication(socket)
                
                inscribe(section_name, socket, server_status, replication_vars)


def check_server_status(process_specs):
    """Checks for a running mysqld process. """
    
    for line in os.popen("ps -ef| grep mysql | grep port=" + process_specs ): 
        fields = line.split()
        pid = fields[0]
        process = fields[4]
    
    if process:
         status = "\t\tRUNNING"
    else:
         status = "\t\tNOT RUNNING"
    
    return status

def check_replication(socket, dbuser, dbpass):
    """Checks slave replication variables."""

    connect = 'mysql -S ' + socket +
              ' --user='+ dbuser +
              '  --password='+ dbpass+
              ' -e "show slave status\\G"'

    result_set =[]
    for line in os.popen(connect):
        field = line.split(':')
        slave_status = field[0].strip()
        result = field[-1].strip()
        #print slave_status,': ', result
        status_of_interest=['Slave_IO_Running',
                            'Slave_SQL_Running',
                            'Last_Errno',
                            'Last_Error',
                            'Last_IO_Errno',
                            'Last_IO_Error']
        if slave_status in status_of_interest:
            #print '\t\t\t\t\t\t',slave_status,': ', result
            result_set.append([slave_status, result])
    
    return result_set


def inscribe(section1, section2, section3, section4):
    print section1, section2, section3, section4 


def notify(stdOut):
    emailTo = []
    emailSubject = "Replication problem on slave " + gethostname()
    emailTo = "aditya.s.mukherjee@gmail.com"
    emailFrom = "inoichi@shinobi.com"
    emailBody = string.join((
                            "From: %s" % emailFrom,
                            "To: %s" % emailTo,
                            "Subject: %s" % emailSubject,
                            "",
                            stdOut
                            ), "\r\n")

    server = smtplib.SMTP("localhost")
    server.sendmail(emailFrom, [emailTo], emailBody)
    server.quit()

def main():
    if len(sys.argv) != 2:
        print "usage: ./inoichi.py filename"
        sys.exit(1)

    filename = sys.argv[1]

    access_instance_setup(filename)

if __name__ == '__main__':
    main()
