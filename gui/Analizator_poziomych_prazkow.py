import cv
import time

class Analizator_poziomych_prazkow:
    def __init__(self, ROI, url,skala, a_gorne, a_dolne, dlugosc_fali , f ,k_grad, C_gorne,C_dolne, konfig, podglad=1, czas=0):
        print "tworze analizator poziomych prazkow"
        self.url = url
        src = url
        try:
            czas=eval(str(czas))
        except:
            czas=1
        ####### WAZNE DLA ZDJECIA##########
        test_freq =konfig[2]
        margin =konfig[4]
        dark_level=konfig[1]
        white_level=konfig[0]
        punkty_na_styczna = 4
        quant_x0=konfig[3] # wieksze od 2 mowi ile pkt poczatkowych biore do wyznaczenia pozycji prazka
        ulamek_koncowkowy =konfig[6]
        gora_dol = konfig[7]
        #TOLERANCJA
        mnoznik=konfig[5]
        self.C_gorne = C_gorne
        self.C_dolne = C_dolne
         
        
        ######### koniec WAZNE DLA ZDJECIA ########## 
        gray , size = self.przygotuj_zdjecie(src, ROI, white_level, dark_level)
        self.pozycje = self.znajdz_ilosc_prazkow(size, test_freq, gray, white_level, dark_level, margin)
        self.odleglosci=[]
        for i in range(len(self.pozycje)):
			self.pozycje[i]=self.pozycje[i]/skala
			if i>0:
				self.odleglosci.append(self.pozycje[i]-self.pozycje[i-1])
			
			
			
        #print "Pozycje kolejnych prazkow:  " , self.pozycje
       
    def daj_string_z_wynikami(self, komentarz):
        wyniki = "Photo: "+self.url +"\n"
        wyniki+= "Data: "+ time.asctime( time.localtime(time.time()) )+ "\n"
        wyniki+= "Distance between fringes: \n"
        wyniki+= "number:      distance[mm]: \n"
        i=0
        self.odleglosci.reverse()
        for odleglosc in self.odleglosci:
            wyniki += str(i)+"-"+str(i+1)+".\t"+str(odleglosc)+"\n"
            i+=1
        return wyniki
        
    def przygotuj_zdjecie(self, src, ROI,white_level, dark_level):

        img = cv.LoadImageM(src,cv.CV_LOAD_IMAGE_COLOR)
        size = cv.GetSize(img)
        print size
        gray = cv.CreateImage(size, 8, 1)
        cv.CvtColor(img, gray, cv.CV_RGB2GRAY)
        print " RRRROOOOIII", ROI
               
        if ROI != [-1,-1,-1,-1]:
		    cv.SetImageROI(gray, (ROI[0],ROI[1],ROI[2],ROI[3]))

        #cv.CvtColor(gray, gay, cv.CV_RGB2GRAY)
        #cv.Threshold(gay,gay, 0, 255, cv.CV_THRESH_BINARY) 
        #cv.Erode(gray,gray)
        #cv.EqualizeHist( gray, gray );
        #cv.Sobel(gray,gray,1,1)
        
        cv.Threshold(gray,gray, white_level*0.8, 255, cv.CV_THRESH_TOZERO)
        cv.Smooth(gray,gray,cv.CV_BLUR,3,1)

        size = cv.GetSize(gray)
        return gray , size

        
    def znajdz_ilosc_prazkow(self, size, test_freq, gray, white_level, dark_level, margin):
        ly=[]      # do tego zapisuje caly rzadek 
        lblack= [] # do tego zapisuje polozenie pikseli <10 a potem kasuje jak juz policze srodek prazka
        lmiddle=[] # do tego zapisuje polozenie srodkow kolejnych prazkow
        llenmidd=[]
        lallmiddles=[]

        j=0
        for py in range(size[0]):  # idzie poziomo
            if py%test_freq==0:
                k=0
                l=0
                for px in range(size[1]): #idzie pionowo
                    l+=1
                    ly.append(gray[px,py])
                    if gray[px,py]>white_level and px>margin and px < size[0]-margin: #jezeli cos jest ciemne i nie lezy po bokach
                        lblack.append(px)
                    
                    if (gray[px,py]<dark_level and gray[px,py-1]<dark_level):  #jezeli 3 piksele obok siebie sa biale
                        if len(lblack)>2:  
		   	                # zakladam ,ze prazek nie moze byc cienszy od 3 pix (2 to minimum, bo inaczej nie policze sredniej)
                            #pxsrednie = sum(lblack)/len(lblack) 
                            pxsrednie = lblack[len(lblack)/2]
                            lmiddle.append(pxsrednie)
                            k+=1  # k liczy ilosc zanotowanych srodkow prazka (ilosc prazkw)
                            #cv.Circle(gray,(pxsrednie,py),2,(255,0,0),2)	
                            lblack=[]    
                j+=1
                llenmidd.append(len(lmiddle))
                lallmiddles.append(lmiddle)
                lmiddle=[]             
        avarage_len = sum(llenmidd)/len(llenmidd)
        #print avarage_len , "to srednia ilosc prazkow"
        return lallmiddles[len(lallmiddles)/2]
        #return avarage_len, llenmidd ,lallmiddles

    def eksportuj_do_pliku_txt(self,string_z_wynikami):
		print "eksportuje do pliku txt"
		txt_file_url = self.url.rsplit(".",2)[0] +".txt"
		txt_file = open(txt_file_url,"w")
		txt_file.write(string_z_wynikami)
		txt_file.close()
		return txt_file_url
