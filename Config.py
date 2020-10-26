from tkinter import *
from tkinter.filedialog import askopenfilename
import tkinter.messagebox
import os
from netmiko import ConnectHandler
from paramiko import AuthenticationException, SSHException, BadHostKeyException
import Read_File
from Read_File import Reading

class Configuration_Import(Frame):
    # Constructor
    def __init__(self):
        # Tkinter Frame Constructor
        Frame.__init__(self)

        # Frame stringVariable access
        self.path = StringVar(self.master)
        self.user = StringVar(self.master)
        self.password = StringVar(self.master)
        self.secr = StringVar(self.master)

        # For listbox items stored as an array
        self.listItem = Variable([])

        #Initialise Variables from method
        self.Frame_Variables()
        self.Widget_Variables()

        self.ipAdd = []
        self.DeviceObjects = []

    # -------------------START OFF TKINTER WIDGET---------------------------------------------
    def Frame_Variables(self):
        # Frame Setup
        self.master.title("Config_Grabber")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.geometry("400x400")
        self.grid(sticky=W + E + N + S)

    # Button configuration
    def Widget_Variables(self):
        # Row 1
        Label(self, text="Path:").pack(expand=True)
        Entry(self, textvariable=self.path).pack(expand=True)  
        self.button = Button(self, text="Import IP List", command=lambda: self.subroutine_ipadd(), width=10)
        self.button.pack()  

        # Row 2
        Label(self, text="Username:").pack()  
        Entry(self, textvariable=self.user).pack()  

        # Row 3
        Label(self, text="Password:").pack()  
        Entry(self, textvariable=self.password, show="*").pack()  

        # Row 4
        Label(self, text="Secret:").pack()  
        Entry(self, textvariable=self.secr, show="*").pack()  

        # Row 5
        Label(self, text="IP:").pack()  
        self.lBox = Listbox(self, listvariable=self.listItem)
        self.lBox.pack()  

        # Row 6
        Button(self, text="Execute",command=lambda: self.executeCom()).pack()  
        Button(self, text="ExcelOutput", command=lambda:self.ipAddLoop()).pack()

    # IP Import Button Call command
    # Will load the file from dialog

    def ipAddLoop(self):
        for i in self.ipAdd:
            Reading((i.replace(".","_")))

    def subroutine_ipadd(self):
        file = self.load_file()
        # Call function to read contents from file and place in listbox
        self.read_contents_file(file)

    # This function will load files to variable from the users set folder
    def load_file(self):
        fname = askopenfilename(filetypes=(("IP Address Files", "*.ipf"),
                                           ("Commands", "*.cmd;*.com"),
                                           ("All files", "*.*")))
        print(fname)
        self.path.set(fname)
        return fname

    # This function will read the variable held with text and remove all unnessasary whitespace
    def read_contents_file(self, file):
        file_contents = open(file, "r")
        for i in file_contents:
            ipAd = i.rstrip()
            ipAd = ipAd.strip('\n')
            ipAd = ipAd.strip()
            self.lBox.insert(END, (ipAd))
            # Append ip addresses to list
            self.ipAdd.append(ipAd)

    # --------------------END OFF TKINTER Widget-----------------------------------------

    # Execution of commands
    def executeCom(self):

        # Get username password and secret to variables
        username = self.user.get()
        password = self.password.get()
        secret = self.secr.get()
        ipAddressCurrentLoop = ""

        # for each ip address in the ListBox

        for ip in self.listItem.get():
            # Append each ip binding the username and password
            self.DeviceObjects.append(Devices(username, password, secret, ip))

        try:
            # For each device object
            for DeviceObj in self.DeviceObjects:
                # Call class which will execute main program using Device object
                ipAddressCurrentLoop = DeviceObj.ip
                CommandsThatHaveExec = CommandExecution(DeviceObj)
                # Output the found ip addresses using cdp neighbours
                print(CommandsThatHaveExec.ipAddressesList)
                self.ipAdd = self.ipAdd + CommandsThatHaveExec.ipAddressesList

            tkinter.messagebox.showinfo("IP Addresses", "\n".join(self.ipAdd))


        except AuthenticationException as authExep:
            tkinter.messagebox.showinfo("Error Auth failure",
                                        "Authentication Failure @ %s \n %s" % (ipAddressCurrentLoop, authExep))
        except SSHException as sshException:
            tkinter.messagebox.showinfo("SSH Host not available",
                                        "Unable to establish SSH connection: %s" % sshException)
        except BadHostKeyException as badHostKeyException:
            print("Bad Host Key", "Unable to verify server's host key: %s" % badHostKeyException)
        except ValueError as ValueErrorException:
            tkinter.messagebox.showinfo("Not available",
                                        "Error: \n%s" % ValueErrorException)

class Devices():
    def __init__(self, username, passw, secr, ip):
        self.username = username
        self.passw = passw
        self.secr = secr
        self.ip = ip
        self.outputFile = "Output/" + (self.ip).replace(".", "_") + ".log"
        print(self.secr)


class CommandExecution():
    def __init__(self, DeviceObject):
        self.commands = ["show ip int brief", "show cdp n d", "show cdp n d | include IP address", "show switch",
                         "show version","show inv","dir","show ver","show vtp status","show vlan","show int status","show etherc sum","show run", "show vlan", "show spann"]  # show arp detail | include ARP entry


        self.ipA = DeviceObject.ip
        self.cisco1 = {"device_type": "cisco_ios",
                       "host": DeviceObject.ip,
                       "username": DeviceObject.username,
                       "password": DeviceObject.passw,
                       "secret": DeviceObject.secr

                       }
        self.ipAddressesList = ""
        self.dirCreation()
        self.commandsToRun()

    def dirCreation(self):
        curPath = os.getcwd()
        print(curPath + "\\" + (str(self.ipA)).replace(".", "_"))
        self.direct = (curPath + "\\" + (str(self.ipA)).replace(".", "_"))
        if (os.path.exists(self.direct)) != True:
            os.mkdir(self.direct)

    def commandsToRun(self):
        for command in self.commands:
            self.Connection(self.cisco1, command)

    def Connection(self, cisco1, command):
        with ConnectHandler(**cisco1) as net_connect:
            net_connect.enable()
            output = net_connect.send_command(command)
            if command == "show cdp n d | include IP address":
                self.IPAddressCDP(output)

        self.writeToFile(command.replace("|", "-"), output)

    def IPAddressCDP(self, output):
        outputList = (output.split())
        # print(outputList)
        outputList = list(set(outputList))
        # print(outputList)
        outputList.remove("IP")
        outputList.remove("address:")
        self.ipAddressesList = outputList

        print("CDP IP",self.ipAddressesList)
        # return outputList

    def writeToFile(self, command, output):
        # fileWritting = open(self.ipA+"_"+command+".log","w")
        fileWritting = open(self.direct + "\\" + command.replace(" ","_") + ".log", "w")
        fileWritting.write((output))
        fileWritting.close()


if __name__ == "__main__":
    Configuration_Import().mainloop()
