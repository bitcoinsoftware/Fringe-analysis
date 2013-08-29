from PyQt4 import QtGui
from Item import Item
from ItemList import ItemList
import Dzialania_na_zdjeciach

class ListWidgetFunctions():
    item_lists_exist=False
    photo_types="jpg gif bmp png jpeg Jpeg Gif tif tiff Bmp Jpg JPG GIF PNG JPEG TIF rgb pbm ppm rast xbm"
    video_types="avi AVI mpeg MPEG mp4 MP4"

	# zaladowanie zdjec i video z folderu
    def add_item(self, url):
        #sprawdzenie po rozszerzeniu czy to filmik czy zdjecie
        url =str(url)
        file_type=url.split(".")
        file_type = (file_type[len(file_type)-1],"")
        
        if not(self.item_lists_exist):
            self.photo_list=ItemList()
            self.video_list=ItemList()
            self.photo_sublist = ItemList()
            self.item_lists_exist=True
            self.photo_types=set(self.photo_types.split())
            self.video_types=set(self.video_types.split()) 
            
        if self.video_types.intersection(file_type):
            print("this is a video")
            self.video_list.append_item(Item(url,self.listWidget_2 , "video_icon.jpg")) 
               
        elif self.photo_types.intersection(file_type):
            print("this is a photo")
            Dzialania_na_zdjeciach.zdejmij_kompresje(url)
            self.photo_list.append_item(Item(url,self.listWidget))
        else:
            print("The " , file_type, " extension is not supported")
            print("Supported extensions: ", self.photo_types, " and ", self.video_types)
            
    
    def get_current_item(self,list_widget,item_list):
		print("get current item")
		return item_list.get_item(list_widget.currentRow())
		
    def get_current_item_index(self,list_widget):
		print("get current item index")
		return list_widget.currentRow()
		
    def get_current_item_url(self,list_widget, item_list):
        return self.get_current_item(list_widget, item_list).url
		
    def remove_item(self,list_widget, itemlist, index):
        print("remove item", index)
        if index>-1:
            list_widget.takeItem(index)
            itemlist.delete_item(index)
        
    def clear_photo_lists(self):
        print("clear_photo_lists")
        a = self.photo_list.len()
        arr=range(a)
        for i in arr:
			a=a-1
			self.remove_item(self.listWidget, self.photo_list,a)
			
    def clear_photo_sublist(self):
        print("clear_photo_SUBlists")
        a = self.photo_sublist.len()
        arr=range(a)
        for i in arr:
			a=a-1
			self.remove_item(self.listWidget_3, self.photo_sublist,a)			
			
		
    def clear_video_lists(self):
        print("clear_video_lists")
        a= self.video_list.len()
        arr= range(a)
        print(arr , a)
        for i in arr:
			a=a-1
			self.remove_item(self.listWidget_2, self.video_list,a)
        
    def remove_all_items(self):
        print("remove all items")
        a = self.photo_list.len()
        arr=range(a)
        for i in arr:
			a=a-1
			self.remove_item(self.listWidget, self.photo_list,a)
			
        a= self.video_list.len()
        arr= range(a)
        print(arr , a)
        for i in arr:
			a=a-1
			self.remove_item(self.listWidget_2, self.video_list,a)
			
    def zmien_rozszerzenie_w_adresie(self,url ,rozszerzenie):
		print "zmien rozszerzenie w adresie"
		return(url.split(".")[0]+"."+rozszerzenie)
		
    def znajdz_czas_pomiaru(self,url_zdjecia):
        #file_name=str(self.listWidget_3.currentItem().text())
        arr = url_zdjecia.split("\\")
        a= len(arr)-1
               
        file_name= arr[a]
        time=file_name.split(".")[0]  #z adresu url wyluskuje numer zdjecia
        folder_path=url_zdjecia.rstrip(file_name)
        try:
            f=open((folder_path+"frame_info.txt"))
            f.readline()
            interval = f.readline().strip()
            f.close()
            time=eval(interval)* eval(time)
        except:
			time = str(time+"*unknown_interval")
        return str(time)
		
		

			
			

