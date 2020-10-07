from netmiko import ConnectHandler
from paramiko import AuthenticationException, SSHException


class getIP:
    def __init__(self,host,username,password,secret):

        #This needs to be set

        #This is used as the starting ip
        self.host = host#"192.168.202.254"

        #Information for cisco
        self.device = "cisco_ios"
        self.username = username#"jfernandes"
        self.password = password#"Flow123456"
        self.secret = secret#"4everPassword1@"
        self.port = 22

        #This variable will hold the switch information e.g Hostname:ip_Address
        self.Switch_Information={}



        self.ciscoDev = {
            'device_type': self.device,
            'host': self.host,
            'username': self.username,
            'password': self.password,
            'port': self.port,  # optional, defaults to 22
            'secret': self.secret,  # optional, defaults to ''
        }

        self.ipListToDo = [self.host]
        self.ipListDone = []
        self.allIPAddresses=[]
        print(self.ipListToDo)



        #self.getIP()


    def getIPDevice(self):
        self.currentip=""
        while (self.ipListToDo != 0) :
            try:
                #if (self.ipListToDo not in self.allIPAddresses):

                #Connect to cisco Device
                #Send command to device
                net_connect = ConnectHandler(**self.ciscoDev)
                output = net_connect.send_command('show cdp n d | include IP address')
                #Output the IP Addresses
                outputL=self.stringCleanUp(output)

                #Start the Enable privillage
                net_connect.enable()


                #Send command
                hostname = net_connect.send_command("show run | include hostname")
                #Clean up the information around the hostname
                hostname=self.hostnameCleanup(hostname)

                #The IP that has had a command already sent to the device
                self.currentip=(self.ciscoDev.get("host"))


                #Store the current ip in a dictonairy
                self.Switch_Information[hostname]=self.currentip

                #Add the ip addresses obtained from the device to list

                self.addAllIpsToBeSearched(outputL)


                #Add the ip addresses which have already been searched
                self.addIpsWhichSearched(self.currentip)
                #self.allIPAddresses.append(self.currentip)
                self.addAllIpsObtained(self.currentip)

                #Remove the ip which has been searched already
                self.ipListToDo.remove(self.currentip)

                #Change the loop to the next ip address
                #Since we got rid of the ip address searched
                self.changeIP(self.ipListToDo[0])
                print("removal:", self.currentip)
                print("IP List to do: ", self.ipListToDo)
                print("IP List Done: ", self.ipListDone)

                #break


            except :

                self.currentip = (self.ciscoDev.get("host"))
                self.allIPAddresses.append(self.currentip)
                print("removal:", self.currentip)
                self.ipListToDo.remove(self.currentip)
                self.changeIP(self.ipListToDo[0])
                print("IP List to do: ",self.ipListToDo)
                print("IP List Done: ", self.ipListDone)
                print("IP List all:", self.allIPAddresses)
                continue

        self.writeToFile()
        return self.ipListDone

    def hostnameCleanup(self,hostname):
        hostname = hostname.replace("hostname", "")
        hostname = hostname.strip()
        return hostname

    def writeToFile(self):
        fileWritting = open("ipAddressList.txt", "w")
        fileWritting.write("\n".join(self.ipListDone))
        fileWritting.close()

    def stringCleanUp(self,output):
        outputL = (output.split())
        outputL = set(outputL)
        outputL.remove("IP")
        outputL.remove("address:")
        outputL = list(outputL)
        return outputL

    def addIpsWhichSearched(self,host):
        self.ipListDone.append(host)
        self.ipListDone=list(dict.fromkeys(self.ipListDone))

    def addAllIpsObtained(self,host):
        self.allIPAddresses.append(host)


    def addAllIpsToBeSearched(self,outList):
        for ip in outList:
            self.ipListToDo.append(ip)
        self.ipListToDo=list(dict.fromkeys(self.ipListToDo))

    def changeIP(self,ipaddress):
        #print(self.ciscoDev)
        self.ciscoDev["host"]=ipaddress
        #print(self.ciscoDev)

    def returnIPList(self):
        return self.ipListDone

    def returnIpDict(self):
        return self.Switch_Information

#Give the name of a failed responce

try:
    ip = getIP("192.168.10.254","netman","4everfw","4everfw")
    ip.getIPDevice()

except Exception as e:
    print(e)
print(ip.returnIpDict())
print(ip.returnIPList())