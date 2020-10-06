import xlsxwriter

f = open("192_168_202_254\dir.log","r")
outputList=(list(f))

workbook = xlsxwriter.Workbook('Expenses01.xlsx')
worksheet = workbook.add_worksheet("dir")


outputList.pop(0)
outputList.pop(1)

netlist=[]
for i in outputList:
    netlist.append(i.split())

netlist.pop(0)
row = 1
col = 0

title=["Size","Permissions","Size2?","Month","Day","Year","Time","GMT","Filename"]
for i in range(9):
    worksheet.write(0,i,title[i])

for file in netlist:
    for col in range(0,len(file)):
        worksheet.write(row, col, file[col])
    row +=1
workbook.close()
