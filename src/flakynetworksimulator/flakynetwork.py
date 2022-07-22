"""
Created by Gauransh Soni on 27th June
Simulation of Variable real life bandwidth situation

"""
# imports
import random
import subprocess
from time import sleep
import os
from time import time
import signal


WIFI_PROFILE = "lte"
MOBILE_DATA = "4g"
TEST_DNS = "127.0.0.1"
PING_DNS = "8.8.8.8"
DROPOUT = "0"
BANDWIDTH_VAR = "0.2"
PING_COUNT = "5"
DEFAULT_MODE = 0
SWITCHES = 2
TIMER = 3
DEBUG_MODE = False
TOUT = 120
JITTERVALUE = 10
BWJITTER=100

# profiles
profiles = {
    "3g":[768,1600,150,0],
    "3gfast":[768,1600,75,0],
    "3gslow":[400,400,200,0],
    "2g":[256,280,400,0],
    "cable":[1000,5000,14,0],
    "dsl":[384,1500,14,0],
    "4g":[9000,9000,85,0],
    "lte":[12000,12000,35,0],
    "edge":[200,240,35,0],    
    "stop":[0,0,1000,0],
    "nospeed":[1000000,1000000,200,0]
}


# Handler to intercept ctrl C request and flush the network rules
def handler(signum, frame):
        print("Processing force stop",signum)
        with open(os.getcwd() + '/py_flaky.log',"a") as outfile:
            subprocess.run("pfctl -f /etc/pf.conf",shell=True, stdout=outfile, stderr=subprocess.STDOUT)
            exit(1)

# def auto_exit_handler(signum,frame):
#     print("Initiating auto exit",signum)
#     flaky.stop()
#     exit(1)

# class flakynetwork
class FlakyNetwork:
    def __init__(self, dns=TEST_DNS, p = MOBILE_DATA):
        self.dns  = dns
        self.p = p
        self.dropout = profiles.get(p)[3]
        self.upspeed = profiles.get(p)[0]
        self.downspeed = profiles.get(p)[1]
        self.dropout = 0.2
        self.ping = profiles.get(p)[2]
        self.ping_count = PING_COUNT
        self.cwd = os.getcwd()
        self.timeout = 120
        signal.signal(signal.SIGINT, handler)
        # signal.signal(signal.SIGALRM, auto_exit_handler)

        with open(self.cwd + '/py_flaky.log',"w") as outfile:
            outfile.write("Flaky network starts \n")

    def setTimeout(self,t):
        self.timeout = t
    
    def __flushThrottler(self):
        try:
            cwd = self.cwd
            with open(cwd + '/py_flaky.log',"a") as outfile:

                subprocess.run(["pfctl" ,"-f" ,"/etc/pf.conf"],stdout=outfile, stderr=subprocess.STDOUT)
                subprocess.run(["dnctl", "-q", "flush"],stdout=outfile, stderr=subprocess.STDOUT)
        except Exception as e:
            with open(cwd +'/py_flaky.log',"a") as outfile:
                outfile.write(e)
            print("Error check logs")
    
    def createProfile(self,name,up,down,ping,dropout):
        profiles[name] = [up,down,ping,dropout]


    def __pingDns(self):
        try:
            cwd = self.cwd
            with open(cwd + '/py_flaky.log',"a") as outfile:
                print("This function is working")
                subprocess.run(["ping", "{dns}".format(dns= self.dns), "-c", "{c}".format(c=self.ping_count)],stdout=outfile, stderr=subprocess.STDOUT)
        except Exception as e:
            with open(cwd +'/py_flaky.log',"a") as outfile:
                outfile.write(e)
            print("Error check logs")

    def __pipeConfig(self,pipe,speed,ping,dropout):
        try:
            return "dnctl pipe {pipe} config bw {speed}Kbits/s delay {ping}ms plr {dropout}".format(speed=speed, pipe = pipe,ping = ping,dropout = dropout)
        except Exception as e:
            with open(cwd +'/py_flaky.log',"a") as outfile:
                outfile.write(e)
            print("Error check logs")
    def pipeConfig(self,pipe,speed,ping,dropout):
        self.__pipeConfig(pipe,speed,ping,dropout)
    def __throttle(self):
        try:
            cwd = self.cwd
            up = self.upspeed
            down = self.downspeed
            ping = self.ping
            dropout = self.dropout
            with open(cwd +'/py_flaky.log',"a") as outfile:
                subprocess.run(self.__pipeConfig(1,up,ping,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                subprocess.run(self.__pipeConfig(2,down,ping,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                subprocess.run("echo \"dummynet in from any to ! 127.0.0.1 pipe 1 \ndummynet out from !127.0.0.1 to any pipe 2\" | sudo pfctl -f -",shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                subprocess.run("pfctl -E",shell=True,stdout=outfile, stderr=subprocess.STDOUT)
        except Exception as e:
            with open(cwd +'/py_flaky.log',"a") as outfile:
                outfile.write(e)
            print("Error check logs")
    def __switch(self, wifi_profile, switches , timer, debug):
        try:
            cwd = self.cwd
            up = self.upspeed
            down = self.downspeed
            ping = self.ping
            dropout = self.dropout
            up_wifi = profiles.get(wifi_profile)[0]
            ping_wifi = profiles.get(wifi_profile)[1]
            dropout_wifi = profiles.get(wifi_profile)[3]
            down_wifi = profiles.get(wifi_profile)[2]
            with open(cwd +'/py_flaky.log',"a") as outfile:
                subprocess.run("dnctl pipe 1 config delay 0ms noerror",shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                subprocess.run("dnctl pipe 2 config delay 0ms noerror",shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                subprocess.run("echo \"dummynet in from any to ! 127.0.0.1 pipe 1 \ndummynet out from !127.0.0.1 to any pipe 2\" | sudo pfctl -f -",shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                # profile 1
                subprocess.run(self.__pipeConfig(1,up,ping,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                subprocess.run(self.__pipeConfig(2,down,ping,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                subprocess.run("pfctl -E",shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                # switch starts-
                for i in range(switches):
                    # Switching to wifi
                    subprocess.run(self.__pipeConfig(1,up_wifi,ping_wifi,dropout_wifi),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                    subprocess.run(self.__pipeConfig(2,down_wifi,ping_wifi,dropout_wifi),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                    sleep(timer)
                    # Switching to mobile data
                    subprocess.run(self.__pipeConfig(1,up,ping,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                    subprocess.run(self.__pipeConfig(2,down,ping,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                    sleep(timer)
        except Exception as e:
            with open(cwd +'/py_flaky.log',"a") as outfile:
                outfile.write(e)
            print("Error check logs")
    def __variableBandwidth(self, var):
        
        try:
            cwd = self.cwd
            up = self.upspeed
            low_up = up - round(up * var)
            high_up = up + round(up*var)
            ping = self.ping
            dropout = self.dropout
            with open(cwd +'/py_flaky.log',"a") as outfile:
                # subprocess.run(["dnctl" ,"pipe", "1", "config", "bw", "{up}Kbit/s".format(up=up), "delay" , "{ping}".format(ping=ping), "plr", "{dropout}".format(dropout=dropout), "noerror"], stdout=outfile,stderr=subprocess.STDOUT) 
                # subprocess.run(" echo 'dummynet in proto {tcp,icmp} from" + " {dns} to any pipe 1' | sudo pfctl -f -".format(dns=self.dns), shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                # subprocess.run(["pfctl", "-e"], stdout=outfile,stderr=subprocess.STDOUT)
                # sleep(4)
                subprocess.run("dnctl pipe 1 config delay 0ms noerror",shell=True)
                subprocess.run(" echo 'dummynet in proto {tcp,icmp} from" + " {dns} to any pipe 1' | sudo pfctl -f -".format(dns=self.dns), shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                subprocess.run(["pfctl", "-e"], stdout=outfile,stderr=subprocess.STDOUT)
                for i in range(5):
                    bw = random.randint(low_up,high_up)
                    subprocess.run(self.__pipeConfig(1,bw,ping,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                    sleep(2)
        except Exception as e:
            with open(cwd +'/py_flaky.log',"a") as outfile:
                outfile.write(e)
            print("Error check logs")
    def __throttleTest(self):
        try:
            cwd = self.cwd
            up = self.upspeed
            ping = self.ping
            dropout = self.dropout
            with open(cwd +'/py_flaky.log',"a") as outfile:
                subprocess.run(self.__pipeConfig(1,up,ping,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                subprocess.run(" echo 'dummynet in proto {tcp,icmp} from" + " {dns} to any pipe 1' | sudo pfctl -f -".format(dns=self.dns), shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                subprocess.run(["pfctl", "-e"], stdout=outfile,stderr=subprocess.STDOUT)
        except Exception as e:
            with open(cwd +'/py_flaky.log',"a") as outfile:
                outfile.write(e)
            print("Error check logs")
    def __switchTest(self, wifi_profile, switches , timer, debug = False):
        try:
            cwd = self.cwd
            up = self.upspeed
            ping = self.ping
            dropout = self.dropout
            # Wifi profile
            up_wifi = profiles.get(wifi_profile)[0]
            ping_wifi = profiles.get(wifi_profile)[1]
            dropout_wifi = profiles.get(wifi_profile)[3]

            with open(cwd +'/py_flaky.log',"a") as outfile:
                subprocess.run(["dnctl" ,"pipe", "1", "config", "bw", "{up}Kbit/s".format(up=up), "delay" , "{ping}".format(ping=ping), "plr", "{dropout}".format(dropout=dropout), "noerror"], stdout=outfile,stderr=subprocess.STDOUT) 
                subprocess.run(" echo 'dummynet in proto {tcp,icmp} from" + " {dns} to any pipe 1' | sudo pfctl -f -".format(dns=self.dns), shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                subprocess.run(["pfctl", "-e"], stdout=outfile,stderr=subprocess.STDOUT)
                # start switching
                for i in range(switches):
                    print("wifi")
                    subprocess.run(self.__pipeConfig(1,up_wifi,ping_wifi,dropout_wifi),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                    sleep(timer)
                    print("mobile data")
                    subprocess.run(self.__pipeConfig(1,up,ping,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                    sleep(timer)    
        except Exception as e:
            with open(cwd +'/py_flaky.log',"a") as outfile:
                outfile.write(e)
            print("Error check logs")
    def __variableBandwitdhTest(self, var = .1):
        try:
            cwd = self.cwd
            up = self.upspeed
            low_up = up - round(up * var)
            high_up = up + round(up*var)
            ping = self.ping
            dropout = self.dropout
            with open(cwd +'/py_flaky.log',"a") as outfile:
                # subprocess.run(["dnctl" ,"pipe", "1", "config", "bw", "{up}Kbit/s".format(up=up), "delay" , "{ping}".format(ping=ping), "plr", "{dropout}".format(dropout=dropout), "noerror"], stdout=outfile,stderr=subprocess.STDOUT) 
                # subprocess.run(" echo 'dummynet in proto {tcp,icmp} from" + " {dns} to any pipe 1' | sudo pfctl -f -".format(dns=self.dns), shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                # subprocess.run(["pfctl", "-e"], stdout=outfile,stderr=subprocess.STDOUT)
                # sleep(4)
                subprocess.run("dnctl pipe 1 config delay 0ms noerror",shell=True)
                subprocess.run(" echo 'dummynet in proto {tcp,icmp} from" + " {dns} to any pipe 1' | sudo pfctl -f -".format(dns=self.dns), shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                subprocess.run(["pfctl", "-e"], stdout=outfile,stderr=subprocess.STDOUT)
                for i in range(5):
                    bw = random.randint(low_up,high_up)
                    subprocess.run(self.__pipeConfig(1,bw,ping,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                    sleep(2)
        except Exception as e:
            with open(cwd +'/py_flaky.log',"a") as outfile:
                outfile.write(e)
            print("Error check logs")
    def stop(self):
        self.__flushThrottler()
    def pingg(self):
        self.__pingDns()
    def set_profile(self,p):
        self.p = p
        self.dropout = profiles.get(p)[3]
        self.upspeed = profiles.get(p)[0]
        self.downspeed = profiles.get(p)[1]
        self.dropout = DROPOUT
        self.ping = profiles.get(p)[2]

    def __random(self,up_a=50,down_a=50,a = 50):
        try:
            cwd = self.cwd
            up = self.upspeed
            down = self.downspeed
            ping = self.ping
            dropout = self.dropout
            tout = 120
            timeout = time() + tout
            with open(cwd +'/py_flaky.log',"a") as outfile:
                subprocess.run("dnctl pipe 1 config delay 0ms noerror",shell=True)
                subprocess.run("dnctl pipe 2 config delay 0ms noerror",shell=True)
                subprocess.run("echo \"dummynet in from any to ! 127.0.0.1 pipe 1 \ndummynet out from !127.0.0.1 to any pipe 2\" | sudo pfctl -f -",shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                subprocess.run(["pfctl", "-e"], stdout=outfile,stderr=subprocess.STDOUT)
                while(True):
                    p = (random.randint(ping -a,ping+a)) // 2
                    u = random.randint(up - up_a, up + up_a)
                    d = random.randint(down - down_a, down + down_a)
                    subprocess.run(self.__pipeConfig(1,u,p,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                    subprocess.run(self.__pipeConfig(2,d,p ,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                    sleep(2)
                    if time() > timeout:
                        break                        
        except:
            print("error check logs")
    def __randomTest(self,up_a=50,down_a=50,a = 50):
        try:
            cwd = self.cwd
            up = self.upspeed
            down = self.downspeed
            ping = self.ping
            dropout = 0
            tout = 120
            timeout = time() + tout
            with open(cwd +'/py_flaky.log',"a") as outfile:
                subprocess.run("dnctl pipe 1 config delay 0ms noerror",shell=True)
                subprocess.run("dnctl pipe 2 config delay 0ms noerror",shell=True)
                subprocess.run(" echo 'dummynet in proto {tcp,icmp} from 172.217.34.194 to any pipe 1 \ndummynet out proto {tcp,icmp} from any to 172.217.34.194 pipe 2' | sudo pfctl -f -", shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                subprocess.run(["pfctl", "-e"], stdout=outfile,stderr=subprocess.STDOUT)
                while(True):
                    p = (random.randint(ping -a,ping+a)) // 2
                    u = random.randint(up - up_a, up + up_a)
                    # d = random.randint(down - down_a, down + down_a)
                    subprocess.run(self.__pipeConfig(1,100000,p,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                    subprocess.run(self.__pipeConfig(2,100000,p,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                    sleep(2)
                    if time() > timeout:
                        break                        
        except Exception as e:
            with open(cwd +'/py_flaky.log',"a") as outfile:
                outfile.write(str(e))
            print("Error check logs")

    def __jitter(self,jittervalue, bwJitter, tout):
        try:
            cwd = self.cwd
            up = self.upspeed
            ping = self.ping
            dropout = self.dropout
            timeout = time() + tout
            with open(cwd +'/py_flaky.log',"a") as outfile:
                    subprocess.run("dnctl pipe 1 config delay 0ms noerror",shell=True)
                    subprocess.run("dnctl pipe 2 config delay 0ms noerror",shell=True)
                    subprocess.run("echo \"dummynet in from any to ! 127.0.0.1 pipe 1 \ndummynet out from !127.0.0.1 to any pipe 2\" | sudo pfctl -f -",shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                    subprocess.run(["pfctl", "-e"], stdout=outfile,stderr=subprocess.STDOUT)
                    while(True):
                        p= random.normalvariate(ping,jittervalue)
                        u = random.normalvariate(up,bwJitter)
                        subprocess.run(self.__pipeConfig(1,u,p,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                        subprocess.run(self.__pipeConfig(2,u,p,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                        sleep(1)
                        if time() >= timeout:
                            break

        except Exception as e:
            with open(cwd +'/py_flaky.log',"a") as outfile:
                outfile.write(e)
            print("Error check logs")   
    def __jitterTest(self, jittervalue, bwjitter, tout):
        try:
            cwd = self.cwd
            up = self.upspeed
            ping = self.ping
            dropout = self.dropout
            timeout = time() + tout
            with open(cwd +'/py_flaky.log',"a") as outfile:
                    subprocess.run("dnctl pipe 1 config delay 0ms noerror",shell=True)
                    subprocess.run(" echo 'dummynet in proto {tcp,icmp} from" + " {dns} to any pipe 1' | sudo pfctl -f -".format(dns=self.dns), shell=True,stdout=outfile, stderr=subprocess.STDOUT)
                    subprocess.run(["pfctl", "-e"], stdout=outfile,stderr=subprocess.STDOUT)
                    while(True):
                        p= random.normalvariate(ping,jittervalue)
                        subprocess.run(self.__pipeConfig(1,up,p,dropout),shell=True,stdout=outfile,stderr=subprocess.STDOUT)
                        sleep(1)
                        if time() >= timeout:
                            break

        except:
            print("Error in jitter check logs")


    def start(self, mode=DEFAULT_MODE,wifi_profile=WIFI_PROFILE, switches = SWITCHES, timer = TIMER, debug = DEBUG_MODE,bw_var = BANDWIDTH_VAR, jittervalue=JITTERVALUE,bwJitter=BWJITTER,tout=TOUT):
        # signal.alarm(self.timeout)
        if(mode==0):
            self.__throttle()
        elif(mode==1):
            self.__variableBandwidth(var=bw_var)
        elif(mode==2):
            self.__switch(switches=switches,timer=timer,wifi_profile=wifi_profile)
        elif(mode==3):
            self.__jitter(jittervalue,bwJitter,tout)
        else:
            print("Mode can only be 0,1,2 or 3")
    
    def test(self, mode=3,wifi_profile=WIFI_PROFILE, switches = SWITCHES, timer = TIMER, debug = DEBUG_MODE, bw_var = BANDWIDTH_VAR, jittervalue=JITTERVALUE,bwJitter=BWJITTER,tout=TOUT):
        # signal.alarm(self.timeout)

        if(mode==0):
            self.__throttleTest()
        elif(mode==1):
            self.__variableBandwitdhTest(var=bw_var)
        elif(mode==2):
            self.__switchTest(switches=switches,timer=timer,wifi_profile=wifi_profile)
        elif(mode==3):
            self.__jitterTest(jittervalue,bwJitter,tout)
        elif(mode==4):
            self.__randomTest()
        else:
            print("Mode can only be 0,1,2 or 3")


# flaky = FlakyNetwork()