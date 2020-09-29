from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
import os
from netmiko import ConnectHandler


class Configuration_Import(Frame):
    # Constructor
    def __init__(self):
        #Tkinter Frame Constructor
        Frame.__init__(self)
        self.Frame_Variables()
        self.Buttons_Variables()
        self.ipAdd=[]
        self.DeviceObjects=[]

#-------------------START OFF TKINTER WIDGET---------------------------------------------
    def Frame_Variables(self):
        #Frame Setup
        self.master.title("Config_Grabber")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.geometry("400x400")
        self.grid(sticky=W + E + N + S)

        #Frame stringVariable access
        self.path=StringVar(self.master)
        self.user=StringVar(self.master)
        self.password=StringVar(self.master)
        self.secr = StringVar(self.master)
        #For listbox items stored as an array
        self.listItem=Variable([])


    #Button configuration
    def Buttons_Variables(self):
        #Row 1
        pathRow=1
        Label(self,text="Path:").grid(row=pathRow,column=0,sticky=W)
        Entry(self,textvariable=self.path).grid(row=pathRow, column=1)
        self.button = Button(self, text="Import IP List", command=lambda :self.subroutine_ipadd(), width=10)
        self.button.grid(row=pathRow, column=2, sticky=E)

        #Row 2
        userRow=2
        Label(self, text="Username:").grid(row=userRow, column=0, sticky=W)
        Entry(self,textvariable=self.user).grid(row=userRow, column=1)

        #Row 3
        passRow=3
        Label(self, text="Password:").grid(row=passRow, column=0, sticky=W)
        Entry(self, textvariable=self.password,show="*").grid(row=passRow, column=1)

        passRow = 4
        Label(self, text="Secret:").grid(row=passRow, column=0, sticky=W)
        Entry(self, textvariable=self.secr, show="*").grid(row=passRow, column=1)

        #Row 5
        ipListRow=5
        Label(self,text="IP:").grid(row=ipListRow,column=0,sticky=W)
        self.lBox=Listbox(self,listvariable=self.listItem)
        self.lBox.grid(row=ipListRow,column=1)

        #Row 6
        executeRow=6
        Button(self,text="Execute",command=lambda:self.executeCom()).grid(row=executeRow,column=0,sticky=W)


    #IP Import Button Call command
    #Will load the file from dialog
    def subroutine_ipadd(self):
        file=self.load_file()
        #Call function to read contents from file and place in listbox
        self.read_contents_file(file)

    def load_file(self):
        fname = askopenfilename(filetypes=(("IP Address Files", "*.ipf"),
                                   ("Commands", "*.cmd;*.com"),
                                   ("All files", "*.*")))
        print(fname)
        self.path.set(fname)
        return fname

    def read_contents_file(self,file):
        file_contents=open(file,"r")
        for i in file_contents:
            ipAd=i.rstrip()
            ipAd=ipAd.strip('\n')
            ipAd=ipAd.strip()
            self.lBox.insert(END,(ipAd))
            self.ipAdd.append(ipAd)


#--------------------END OFF TKINTER Widget-----------------------------------------


    #Execution of commands
    def executeCom(self):
        username=self.user.get()
        password=self.password.get()
        secret=self.secr.get()
        for ip in self.listItem.get():
            self.DeviceObjects.append(Devices(username,password,secret,ip))
        for DeviceObj in self.DeviceObjects:
            CommandExecution(DeviceObj)






class Devices():
    def __init__(self,username,passw,secr,ip):
        self.username=username
        self.passw=passw
        self.secr=secr
        self.ip=ip
        self.outputFile="Output/"+(self.ip).replace(".","_")+".log"

class CommandExecution():
    def __init__(self,DeviceObject):
        self.commands=["show ip int brief", "show cdp n", "show switch", "show version", "show vlan","show spann"] #show arp detail | include ARP entry
        self.ipA=DeviceObject.ip
        self.cisco1={"device_type":"cisco_ios",
                "host":DeviceObject.ip,
                "username":DeviceObject.username,
                "password":DeviceObject.passw,

        }
        self.commandsToRun()

    def commandsToRun(self):
        for command in self.commands:
            self.Connection(self.cisco1,command)

    def Connection(self,cisco1,command):
        with ConnectHandler(**cisco1) as net_connect:
            output = net_connect.send_command(command)
        print(command)
        print(output)
        self.writeToFile(command.replace("|","-"),output)

    def writeToFile(self,command,output):
        fileWritting = open(self.ipA+"_"+command+".log","w")
        fileWritting.write(output)
        fileWritting.close()


if __name__ == "__main__":
    Configuration_Import().mainloop()
