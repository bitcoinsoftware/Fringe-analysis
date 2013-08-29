from PyQt4 import QtGui , QtCore

class Item():
    
    index= 0
    item = ""
    icon = ""
    name = ""
    url = ""
    list = ""
    size = [50,50]
	
	
    def __init__(self, url , list, icon_url=None):
        self.url = url
        self.list = list
        self.icon = QtGui.QIcon()
        qsize = QtCore.QSize(self.size[0],self.size[1])
        if icon_url:
            self.icon.addFile(icon_url, qsize)
        else:
            self.icon.addFile(url, qsize)	
        #wersja dosowa
        name = url.split("\\")
        # wersja unixowa
        if len(name)==1:
            name= url.split("//")
        #
        self.name = name [len(name)-1]
	
        self.item = QtGui.QListWidgetItem(self.icon, self.name, self.list)
        
    def set_item_index(self,index):
		self.index=index

