import PySimpleGUI as sg

sg.popup('find')
sg.popup("数据汇总完成，请打开表格查看{}工作表(xlsx)或程序同级目录下的{}工作簿(xls)".format(self.sheetName, self.sheetName), font=("微软雅黑", 12), title='提示')