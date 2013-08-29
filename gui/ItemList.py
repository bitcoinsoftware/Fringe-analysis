from PyQt4 import QtGui , QtCore

class ItemList():
    def __init__(self):
        self.itemlist= []

    def append_item(self, item):
        self.itemlist.append(item)
        item.set_item_index(len(self.itemlist)-1)
        
    def pop_item(self):
        self.itemlist.pop()
        
    def delete_item(self, index):
		self.itemlist.pop(index)
		print("Now the item list looks like this: " , self.itemlist)
		
    def get_item(self,index):
		return self.itemlist[index]
        
    def get_item_url(self, index):
		return self.itemlist[index].url
		
    def len(self):
		return len(self.itemlist)
    
