import os
import thread
import time
#import threading
from Camera import *
from ListWidgetFunctions import *
from FolderWithItems import *
from Analizator_prazkow import *
from QGraphicsScene2 import *
from Skalownik import *
from HistogramItem import *
from PyQt4.Qwt5 import *
from PyQt4 import QtCore, QtGui
from Analizator_poziomych_prazkow import *

class GuiFunctions(ListWidgetFunctions):
    current_photo_item= ""
    current_video_item= ""
    width = 708
    height=541
    cam_on_off = 0

    sublistwidget_active=0  # 1 - main , 2 - sub

    def save_scale(self):
        print "save scale"
        try:
            self.skala = self.doubleSpinBox_9.value()
            url = "config.txt"
            file = open(url,"r")
            lista_linii =""
            for line in file:
                if line.split("=")[0] =="skala":
                    line = "skala="+str(self.skala)+"\n"
                print line
                lista_linii+=line
            file.close()
            file = open(url,"w")
            file.write(lista_linii)
            file.close()
        except:
            print "Coud not open or read config.txt file"

    def make_frames_from_video(self):
        print "make frames from video"
        try:
            video_url=self.get_current_item(self.listWidget_2, self.video_list).url
            if (video_url.split(".")[1]).strip()!="wmv":
                interval = 1000* self.spinBox_4.value()
                extension= "\'.bmp\'"
                a=video_url.split("\\")
                i=len(a)
                if i>0:
                    prefix="{"+a[i-1]+"}"
                new_dir_url= video_url.split(".")[0]+"frames"+(time.asctime( time.localtime(time.time()) ).replace(" ","_")).replace(":","_")
                os.makedirs(new_dir_url)
            
                info_file=new_dir_url+"\\frame_info.txt"
                f = open(info_file,"w")
                informacje_o_klatkowaniu= video_url +"\n" +str(interval)
                f.write(informacje_o_klatkowaniu)
                f.close()
                start_frame_making_program = "start "+os.path.abspath('')+"\\FrameCapture.exe" + " " +video_url + " " + new_dir_url + " "+str(interval)+" "+ extension
                print start_frame_making_program
                thread.start_new_thread(os.system, (start_frame_making_program,))
        except:
			print "Coud not make frames from video"
    	     
    def turn_camera_on(self):
        try:
            start_camera_program = "start "+os.path.abspath('')+"\Program_kamery\IC_Capture.exe"
            thread.start_new_thread(os.system, (start_camera_program,))	
        except:
			print "Could not turn camera on"	    
      
    def exit_program(self):
        print "exit"
        quit()
                     		
    def open_workspace(self):
        print("open workspace")
        try:
            workspace_url = os.path.abspath('')+"\..\workspace"
            command = "explorer " +workspace_url
            thread.start_new_thread(os.system,(command,))
        except:
			print "Could not open workspace"
         
    def edit_photo(self):       
        editor = "start "+os.path.abspath('')+ "\Program_edycji_zdjecia\\bin\\gimp-2.6.exe "+self.get_current_item_url(self.listWidget, self.photo_list)
        try:
            thread.start_new_thread(os.system,(editor,))
        except:
            print ("gimp sie nie wlaczyl")
            
    def delete_photo(self):
		try:
		    if self.photo_list.len()>0:
		        url = self.get_current_item(self.listWidget, self.photo_list).url
		        print("You want do delete this file: ",url )
		        index= self.get_current_item_index(self.listWidget)
		        self.delete_item_from_hdd(url)
		        self.remove_item(self.listWidget, self.photo_list, index)
		    print("delete photo")
		except:
			print "Could not delete the photo"

    def add_to_sublist(self):
        try:
            print "add to sub list"
            self.sublistwidget_active=1   #ktory widget zdjeciowy aktywny
            if self.radioButton_3.isChecked():
                try:
                    self.graphic_scene.status=True
                except:
			        print "graphic_scene nie istnieje"
            url = self.get_current_item(self.listWidget, self.photo_list).url
            self.photo_sublist.append_item(Item(url, self.listWidget_3))
        except:
		    print "Could not add to sublist"
		   
    def add_all_to_photo_sublist(self):
        print "add all to sublist"
        self.sublistwidget_active=1   #ktory widget zdjeciowy aktywny
        if self.radioButton_3.isChecked():
            try:
                self.graphic_scene.status=True
            except:
			    print "graphic_scene nie istnieje"
        arr= range(self.listWidget.count())
        for i in arr: 
            url =self.photo_list.get_item_url(i)
            self.photo_sublist.append_item(Item(url, self.listWidget_3))            
			    
    def remove_from_sublist(self):
        print "remove from sublist"
        self.remove_item(self.listWidget_3, self.photo_sublist, self.get_current_item_index(self.listWidget_3))
        
    def save_subresults(self):
        try:
            print "sub results"
            results = ""
       
            a = self.listWidget_5.count()
            arr=range(a)
            for i in arr:
			    a=a-1
			    results+=self.listWidget_5.item(a).text().split(":")[1]+"\n"
            f_url = QtGui.QFileDialog.getSaveFileName(directory="..\workspace")
            if f_url!="":
                file=open(f_url,"w")
        
                if self.radioButton_3.isChecked():# jesli zaznaczony radiobutt od Imbalance
			        wektory = self.licz_wektor(results)
			        results +="Shift vector: "+ str(wektory[0])+ "[mm]\n"
			        results +="Velocity vector: "+ str(wektory[1])+"[mm/ms]\n"
			
                if self.radioButton_4.isChecked(): # jesli zaznaczony C change
                    zmiana_C, szybkosc = self.licz_zmiane_C(results)
                    results+="Change of C: "+str(zmiana_C)+"\n"
                    results+= "Speed of C change: " + str(szybkosc)+"[/ms]\n"
                    results += "Distance from the edge of region of interest: " + str(self.doubleSpinBox_11.value())+"\n"
		
                file.write(results)
                file.close()
        except:
			print "Sub results could not be saved"
    def set_criterion_value(self):
        print "set criterion value"
        if self.radioButton_5.isChecked():
            self.doubleSpinBox_6.setValue(0.0001)
        elif self.radioButton_6.isChecked():
            self.doubleSpinBox_6.setValue(50.0)
        elif self.radioButton_7.isChecked():
            self.doubleSpinBox_6.setValue(1.0)
        
        
        
    def licz_zmiane_C(self,results):
        print "licz zmiane C"
        pierwszy=0
        ostatni=0
        print results
        linie = str(results).split("\n")
        for i in range(len(linie)):
            if len(linie[i])>5:  #zabezpieczam sie przed pustymi polami na koncu
                wartosci=linie[i].rsplit(" ")
                wartosc =eval(wartosci[0])
                if i==0:
                    pierwszy = 0
                    minimalny = wartosc
                    ostatni = 0
                    maksymalny = wartosc
                else:
                    if wartosc<minimalny:
                        minimalny = wartosc
                        pierwszy = i
                    elif wartosc>maksymalny:
                        maksymalny = wartosc
                        ostatni = i
        #print "pierwsze polozenie  " , linie[pierwszy] , "  ostatnie polozenie  ", linie[ostatni]
        delta_t = eval(linie[ostatni].split(" ")[0]) - eval(linie[pierwszy].split(" ")[0])
        delta_C = eval(linie[ostatni].split(" ")[1]) - eval(linie[pierwszy].split(" ")[1])
        if delta_t>0:
            szybkosc_zmiany = delta_C/ float(delta_t)
        else: 
            szybkosc_zmiany = 0
            
        print "zmiana C : " , delta_C
        return delta_C, szybkosc_zmiany
		
    def licz_wektor(self,results):
        print "licz wektor"
        pierwszy=0
        ostatni=0
        print results
        linie = str(results).split("\n")
        for i in range(len(linie)):
            if len(linie[i])>5:  #zabezpieczam sie przed pustymi polami na koncu
                wartosci=linie[i].rsplit(" ")
                wartosc =eval(wartosci[0])
                if i==0:
                    pierwszy = 0
                    minimalny = wartosc
                    ostatni = 0
                    maksymalny = wartosc
                else:
                    if wartosc<minimalny:
                        minimalny = wartosc
                        pierwszy = i
                    elif wartosc>maksymalny:
                        maksymalny = wartosc
                        ostatni = i
        #print "pierwsze polozenie  " , linie[pierwszy] , "  ostatnie polozenie  ", linie[ostatni]
        delta_t = eval(linie[ostatni].split(" ")[0]) - eval(linie[pierwszy].split(" ")[0])
        delta_x = eval(linie[ostatni].split(" ")[1]) - eval(linie[pierwszy].split(" ")[1])
        delta_y = eval(linie[ostatni].split(" ")[2]) - eval(linie[pierwszy].split(" ")[2])
        wektor_przesuniecia = [delta_x, delta_y]
        wektor_predkosci = [wektor_przesuniecia[0]/float(delta_t), wektor_przesuniecia[1]/float(delta_t)]
        print "wektor przesuniecia " , wektor_przesuniecia , " wektor predkosci " , wektor_predkosci
        return [wektor_przesuniecia, wektor_predkosci]
        		
    def clear_subresults(self):
        a = self.listWidget_5.count()
        arr=range(a)
        for i in arr:
			a=a-1
			self.listWidget_5.takeItem(a)

    def insert_to_resultlistwidget(self,x,y):
        print "insert to resultlistwidget"
        photo_url = self.get_current_item_url(self.listWidget_3, self.photo_sublist)
        #time = photo_url.split("\\")[len(photo_url.split("\\"))-1]
        
        file_name=str(self.listWidget_3.currentItem().text())
        time=file_name.split(".")[0]  #z adresu url wyluskuje numer zdjecia
        folder_path=photo_url.rstrip(file_name)
        try:
            f=open((folder_path+"frame_info.txt"))
            f.readline()
            interval = f.readline().strip()
            f.close()
            time=eval(interval)* eval(time)
        except:
			time = str(time+"*interval")
        
        self.listWidget_5.addItem(("Time[ms],x,y[mm]:"+str(time)+" "+str(x/self.skala)+" "+str(y/self.skala)))

    def display_sublist_photo(self):
        print("dispaly SUBpicture")
        self.sublistwidget_active=1   #ktory widget zdjeciowy aktywny
        print (self.radioButton_3.isChecked() and self.sublistwidget_active)
        self.graphic_scene = QGraphicsScene2((self.radioButton_3.isChecked() and self.sublistwidget_active), self.graphicsView, self.insert_to_resultlistwidget)

        self.graphicsView.setScene(self.graphic_scene)
        url =self.get_current_item_url(self.listWidget_3, self.photo_sublist)
        qpixmap = QtGui.QPixmap(url)

        self.graphic_scene.set_display_widget(self.graphicsView,qpixmap.width(),qpixmap.height())
        print url	
        
        #Jesli zdjecie mniejsze od rozmiarow display
        if qpixmap.width()<self.width:
			self.graphic_scene.x_move = (self.width- qpixmap.width())/2
        if qpixmap.height()<self.height:
			self.graphic_scene.y_move = (self.height- qpixmap.height())/2	
	
        #Jesli zdjecie wieksze od rozmiarow display
        if qpixmap.width()>self.width:
            print "PRZESKALOWANE"
            self.graphic_scene.skala_zdjecia = self.width/float(qpixmap.width())
            item =QtGui.QGraphicsPixmapItem(QtGui.QPixmap(url).scaledToWidth(self.width))
            self.qpixmap_width = int(qpixmap.width()*self.graphic_scene.skala_zdjecia)
            self.qpixmap_height = int(qpixmap.height()*self.graphic_scene.skala_zdjecia) 
             
            if self.qpixmap_height<self.height:
			    self.graphic_scene.y_move = (self.height- self.qpixmap_height)/2         
        else:
            item =QtGui.QGraphicsPixmapItem(QtGui.QPixmap(url))        
		
        self.graphic_scene.addItem(item)
        self.graphicsView.show()		
		     
    def display_photo(self):
        print("dispaly picture")
        self.sublistwidget_active=0
        self.graphic_scene = QGraphicsScene2((self.radioButton_3.isChecked() and self.sublistwidget_active),self.graphicsView)

        self.graphicsView.setScene(self.graphic_scene)
        url =self.get_current_item_url(self.listWidget, self.photo_list)
        qpixmap = QtGui.QPixmap(url)

        self.graphic_scene.set_display_widget(self.graphicsView,qpixmap.width(),qpixmap.height())
        print url	
        
        #Jesli zdjecie mniejsze od rozmiarow display
        if qpixmap.width()<self.width:
			self.graphic_scene.x_move = (self.width- qpixmap.width())/2
        if qpixmap.height()<self.height:
			self.graphic_scene.y_move = (self.height- qpixmap.height())/2	
	
        #Jesli zdjecie wieksze od rozmiarow display
        if qpixmap.width()>self.width:
            print "PRZESKALOWANE"
            self.graphic_scene.skala_zdjecia = self.width/float(qpixmap.width())
            item =QtGui.QGraphicsPixmapItem(QtGui.QPixmap(url).scaledToWidth(self.width))
            self.qpixmap_width = int(qpixmap.width()*self.graphic_scene.skala_zdjecia)
            self.qpixmap_height = int(qpixmap.height()*self.graphic_scene.skala_zdjecia) 
             
            if self.qpixmap_height<self.height:
			    self.graphic_scene.y_move = (self.height- self.qpixmap_height)/2         
        else:
            item =QtGui.QGraphicsPixmapItem(QtGui.QPixmap(url))        
		
        self.graphic_scene.addItem(item)
        self.graphicsView.show()

    def display_video_info(self):
        print "display_video_info"
        graphic_scene = QGraphicsScene2(self.graphicsView_2)

        self.graphicsView_2.setScene(graphic_scene)
        #folder_path=str(QtGui.QFileDialog.getExistingDirectory(directory="."))
        url =os.path.abspath('')+"\\"+"video_icon.bmp"
        print url
        qpixmap = QtGui.QPixmap(url)
        if qpixmap.width()>self.width:
			item =QtGui.QGraphicsPixmapItem(QtGui.QPixmap(url).scaledToWidth(self.width))
        else:
            item =QtGui.QGraphicsPixmapItem(QtGui.QPixmap(url))
        graphic_scene.addItem(item)
        self.graphicsView_2.show()
        url = self.get_current_item(self.listWidget_2, self.video_list).url
        self.addFiles(url)
   
    def load_pictures(self):
        print "load_pictures"
        folder_path=str(QtGui.QFileDialog.getExistingDirectory(directory="..\workspace"))
        if folder_path =="":
			return 0 
        print folder_path
        folder_path= folder_path + "\\"
        folder_path_list=[]
        folder_list=[]
        
        folder= FolderWithItems(folder_path)
        folder_list.append(folder)
        folder_path_list.append(folder_path)
        
        try:
            list_of_files = os.listdir(folder_path) 
        except IOError as (errno, strerror):
            print "I/O error({0}): {1}".format(errno, strerror)
        except ValueError:
            print "Could not convert data to an integer."
        except:
            print "Unexpected error:", sys.exc_info()[0]
        for file_object in list_of_files:	       
            try: 				
                item_path=folder_path  + file_object
                print("zdjecie znajduje sie w" ,item_path)
                self.add_item(item_path)
            except:
                print("could not add: " , item_path ," to list widget")
                
        #thread.start_new_thread(self.update_listwidgets2, (folder_list,)) 	       
    def load_video(self):
        print "load video"
        self.add_item(QtGui.QFileDialog.getOpenFileName(directory="..\workspace"))
        
    def remove_all_photos(self):
		print "remove all photos"
		self.clear_photo_lists()
		
    def remove_all_videos(self):
		print "remove all videos"
		self.clear_video_lists()
				
    def delete_video(self):
        try:
		    if self.video_list.len()>0:
		        url = self.get_current_item(self.listWidget_2, self.video_list).url
		        print("You want do delete this file: ",url )
		        index= self.get_current_item_index(self.listWidget_2)
		        self.delete_item_from_hdd(url)
		        self.remove_item(self.listWidget_2, self.video_list, index)
		    print("delete video")
        except:
			print("could not delete video")
			
	
#################################	          
    def delete_item_from_hdd(self, url):	
        try:
            print("wyrzucam zdjecie")
            remove_file="rm " + url
            thread.start_new_thread(os.system, (remove_file,))
        except:
            print("nie udalo sie wyrzucic zdjecia")
            
    def update_listwidgets2(self,folder_list):
        import time
        print("update listwidgets")
        #tutaj dla kazdego folderu robie sprawdzenie co 3 sek czy sie zmienila jego zawartosc
        while 1:
            for folder in folder_list:
                if folder.conntent_changed():
                    print(folder.path, "conntent changed")
                    self.remove_all_items()
                    for folder in folder_list:
                        # dodanie zdjec i video do widgetow
                        for file_object in os.listdir(folder.path):	        
                            try: 				
                                item_path=folder.path  + file_object
                                print(item_path)
                                self.add_item(item_path)
                            except:
                                print("could not add: " , item_path ," to list widget")
                    continue
				    
            time.sleep(3)

    def item_analysis(self):
        print("odpalam program do analizy")
        a_gorne =		self.doubleSpinBox_3.value()
        a_dolne = 		self.doubleSpinBox_4.value()
        dlugosc_fali = 	self.doubleSpinBox_2.value()
        f = 			self.doubleSpinBox_5.value()
        szerokosc_membrany = self.doubleSpinBox_12.value()
        k_grad = 		self.doubleSpinBox_6.value()
        C_gorne =		self.doubleSpinBox_7.value()
        C_dolne = 		self.doubleSpinBox_8.value()
        komentarz = 	self.plainTextEdit.toPlainText()
        gora_dol = [self.checkBox_2.isChecked(),self.checkBox.isChecked()]

        white_level= self.horizontalSlider.value()
        #dark_level= self.horizontalSlider_2.value()
        dark_level= 64
        test_period= self.spinBox.value()
        #starting_points = self.spinBox_2.value()
        starting_points = 10
        #margin = self.spinBox_3.value()
        margin = 0
        #diff_coeff = self.doubleSpinBox_9.value()
        diff_coeff = 0.70
        #tangend_coeff = self.doubleSpinBox_10.value()
        tangend_coeff = 0.50
        
        if self.radioButton_5.isChecked():
            rodzaj_kryterium = 0
        elif self.radioButton_6.isChecked():
            rodzaj_kryterium =1
        elif self.radioButton_7.isChecked():
            rodzaj_kryterium =2
        
        try:   
        
            dane = [white_level,dark_level,test_period,starting_points,margin,diff_coeff,tangend_coeff,gora_dol,szerokosc_membrany]
            url = self.get_current_item_url(self.listWidget, self.photo_list)
            time=self.znajdz_czas_pomiaru(url)
            if self.radioButton_2.isChecked():
			
                anal = Analizator_prazkow(self.graphic_scene.ROI,url,self.skala ,a_gorne, a_dolne, dlugosc_fali , f ,k_grad, C_gorne,C_dolne,dane,podglad=1,czas=time,  rodzaj_kryterium=rodzaj_kryterium)
        
                anal.eksportuj_do_pliku_txt(anal.daj_string_z_wynikami(komentarz))
                argumenty=[]
                wartosci=[]
                argumenty.append(anal.wyniki_gorne[0])
                argumenty.append(anal.wyniki_dolne[0])
                wartosci.append(anal.wyniki_gorne[1])
                wartosci.append(anal.wyniki_dolne[1])
        
                self.rysuj_wykres(argumenty,wartosci,self.skala)
            elif self.radioButton.isChecked():
                anal = Analizator_poziomych_prazkow(self.graphic_scene.ROI,url,self.skala ,a_gorne, a_dolne, dlugosc_fali , f ,k_grad, C_gorne,C_dolne,dane,podglad=1,czas=time)
                txt_url =anal.eksportuj_do_pliku_txt(anal.daj_string_z_wynikami(komentarz))
                komenda = "notepad "+txt_url
                thread.start_new_thread(os.system, (komenda,))
        except:
			print "Could not perform item analysis"
        
    def time_item_analysis(self):
        try:
		    thread.start_new_thread(self.time_c_analysis,())
        except:
			print "could not perform time c analysis"
		
    def time_c_analysis(self):
        if self.radioButton_5.isChecked():
            rodzaj_kryterium = 0
        elif self.radioButton_6.isChecked():
            rodzaj_kryterium =1
        elif self.radioButton_7.isChecked():
            rodzaj_kryterium =2
        
        if self.radioButton_4.isChecked():
            height = self.doubleSpinBox_11.value()
            print("odpalam program do analizy")
            a_gorne =		self.doubleSpinBox_3.value()
            a_dolne = 		self.doubleSpinBox_4.value()
            dlugosc_fali = 	self.doubleSpinBox_2.value()
            f = 			self.doubleSpinBox_5.value()
            szerokosc_membrany = self.doubleSpinBox_12.value()
            k_grad = 		self.doubleSpinBox_6.value()
            C_gorne =		self.doubleSpinBox_7.value()
            C_dolne = 		self.doubleSpinBox_8.value()
            komentarz = 	self.plainTextEdit.toPlainText()
            gora_dol = [self.checkBox_2.isChecked(),self.checkBox.isChecked()]

            white_level= self.horizontalSlider.value()
            #dark_level= self.horizontalSlider_2.value()
            dark_level= 64
            test_period= self.spinBox.value()
            #starting_points = self.spinBox_2.value()
            starting_points = 10
            #margin = self.spinBox_3.value()
            margin = 0
            #diff_coeff = self.doubleSpinBox_9.value()
            diff_coeff = 0.70
            #tangend_coeff = self.doubleSpinBox_10.value()
            tangend_coeff = 0.50
        
            dane = [white_level,dark_level,test_period,starting_points,margin,diff_coeff,tangend_coeff,gora_dol,szerokosc_membrany]
        
            arr= range(self.listWidget_3.count())
            if self.radioButton.isChecked():
                if len(arr)>0:
                    folder_url=""
                    skladowe = self.photo_sublist.get_item_url(0).split("\\")
                    for i  in range(len(skladowe)-1):
						folder_url += (skladowe[i]+"\\")
						
                    command = "explorer " +folder_url
                    thread.start_new_thread(os.system,(command,))                
				    
                for i in arr: 
                    url =self.photo_sublist.get_item_url(i)
                    time=self.znajdz_czas_pomiaru(url)
                    print "horizontal analysis"
                    anal = Analizator_poziomych_prazkow(self.graphic_scene.ROI,url,self.skala ,a_gorne, a_dolne, dlugosc_fali , f ,k_grad, C_gorne,C_dolne,dane,podglad=1,czas=time)
                    txt_url = anal.eksportuj_do_pliku_txt(anal.daj_string_z_wynikami(komentarz))              
            else:
                for i in arr: 
                    url =self.photo_sublist.get_item_url(i)
                    time=self.znajdz_czas_pomiaru(url)
                    anal = Analizator_prazkow(self.graphic_scene.ROI,url,self.skala ,a_gorne, a_dolne, dlugosc_fali , f ,k_grad, C_gorne,C_dolne,dane,podglad=0,czas=time,  rodzaj_kryterium=rodzaj_kryterium)
                    anal.eksportuj_do_pliku_txt(anal.daj_string_z_wynikami(komentarz))
            
                    url_tekstowego =self.zmien_rozszerzenie_w_adresie(url,"txt")
                    print "wysokosc na ktorej badam to: ",height
                    #f=open(url_tekstowego)
                    wartosc = anal.znajdz_wartosc_w_tekstowym_na_wysokosci(url_tekstowego, gora_dol, height)
                    self.listWidget_5.addItem(("Time[ms],C[j]:"+str(time)+" "+str(wartosc)))
        		
    def scale(self):
        print "Scale"
        try:
            skalownik =Skalownik(self.graphic_scene.ROI,self.get_current_item_url(self.listWidget, self.photo_list))
            srednica_w_pix= skalownik.get_diameter()
            srednica_rzeczywista = self.doubleSpinBox.value()
            self.skala = round(srednica_w_pix / srednica_rzeczywista,2)
            #tekst = "Scale :   "+ str(self.skala)+" [ pix / mm]"
            #self.label_3.setText(QtGui.QApplication.translate("MainWindow", tekst, None, QtGui.QApplication.UnicodeUTF8))
            self.doubleSpinBox_9.setValue(self.skala)
        except:
			print "Could not scale"
        
    def rysuj_wykres(self,wartosci, argumenty, skala):
        try:
            if (len(wartosci[0])>0 or len(wartosci[1])>0):
                try:
                    self.qwtPlot.hide()
                    self.qwtPlot.destroy()
                except:
				    print "plot not created before"
        
                self.qwtPlot = QwtPlot(self.centralwidget)
                self.qwtPlot.setGeometry(QtCore.QRect(860, 69, 491,380))
                self.qwtPlot.setObjectName("qwtPlot")
         
                skx= []
                sky_min= []
                sky_max= []
                for args in argumenty:
			        if len(args)!=0:
				        skx.append(max(args))
                for wart in wartosci:
			        if len(wart)!=0:
				        sky_min.append(min(wart))
				        sky_max.append(max(wart))

                self.qwtPlot.setAxisScale(QwtPlot.yLeft ,  min(sky_min), max(sky_max))
                self.qwtPlot.setAxisTitle(QwtPlot.yLeft, "C")
                self.qwtPlot.setAxisScale(QwtPlot.xBottom,  0.0,max(skx))
                self.qwtPlot.setAxisTitle(QwtPlot.xBottom,"Distance [mm]")
        
                grid = Qwt.QwtPlotGrid()
                grid.enableXMin(True)
                grid.enableYMin(True)
                grid.setMajPen(QtGui.QPen(QtGui.QColor(0,0,0), 1));
                #grid.setMinPen(QtGui.QPen(QtGui.QColor(100,100,100), 1));
     
                grid.attach(self.qwtPlot)
                
                self.doubleSpinBox_11.setMaximum(max(skx))

                #histogram = HistogramItem()
                #histogram.setColor(QtGui.QColor(170,170,100))
                i=0
                for args in argumenty:
                    curve = QwtPlotCurve("Curve "+str(i))
                    curve.setData(args, wartosci[i])
                    #print args , "ARGUMENTY" ,type(args)
                    #print wartosci[i], "WARTOSCI", type(wartosci[i])
                    curve.attach(self.qwtPlot)
                    i+=1
        
                self.qwtPlot.replot()
    
                self.qwtPlot.show()
        except:
			print("could not draw chart")
 

