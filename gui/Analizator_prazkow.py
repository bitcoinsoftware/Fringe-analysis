import cv
import math
#import pylab
import thread
import time
from scipy import ndimage
from PIL import ImageEnhance

class Analizator_prazkow:
    zasieg_dyfuzji_dol=0
    zasieg_dyfuzji_gora=0
    ilosc_substancji_dol = 0
    ilosc_substancji_gora = 0
    strumien_gora=0
    strumien_dol=0
    wspolczynnik_dyfuzji_gora = 0
    wspolczynnik_dyfuzji_dol = 0
    

    def __init__(self, ROI, url,skala, a_gorne, a_dolne, dlugosc_fali , f ,k_grad, C_gorne,C_dolne, konfig, podglad=1,czas=1,  rodzaj_kryterium=0):
        print "tworze analizator prazkow"
        self.url = url
        src = url
        try:
            czas = eval(czas)
        except:
            czas=1
        ####### WAZNE DLA ZDJECIA##########
        # dane wazne w analizie zdjec
        test_freq =konfig[2]  # co ile pikseli sprawdza wartosc
        margin =konfig[4]     # margines gora dol boki
        dark_level=konfig[1]  # prog uznawania za czarny
        white_level=konfig[0] #prog uznawania za bialy
        punkty_na_styczna = 4 # z ilu punktow wyliczam styczna dynamiczna 
        quant_x0=konfig[3] # wieksze od 2 mowi ile pkt poczatkowych biore do wyznaczenia pozycji prazka
        ulamek_koncowkowy =konfig[6]  # decyduje jaka czesc wszystkich punktow prazka przeznaczyc na styczna statyczna
        gora_dol = konfig[7] # mowi czy wybralismy do analizy gorne prazki czy dolne
        szerokosc_membrany= konfig[8] #wlasciwie to nic nie robi - relikt przeszlosci
        #TOLERANCJA
        mnoznik=konfig[5] #
        self.C_gorne = C_gorne  #poczatkowa wartosc gornego C
        self.C_dolne = C_dolne  #poczatkowa wartosc dolnego C
        ######### koniec WAZNE DLA ZDJECIA ########## 
        
        #przygotowuje zdjecie progujac i latajac dziury w prazkach
        gray , size = self.przygotuj_zdjecie(src, ROI, white_level, dark_level)
        
        #definiuje poczatkowe prazki do ktorych beda dopasowywane pozostale punkty charakterystyczne
        avarage_len , llenmidd, lallmiddles = self.znajdz_ilosc_gornych_prazkow(size, test_freq, gray, white_level, dark_level, margin)
        #print "srodkowy prazek ma numer", avarage_len/2
        numer_prazka=avarage_len/2
        
        #znajduje na jakiej wysokosci jest membrana
        ymembrana ,ymembranaP ,ymembranaK =  self.znajdz_wysokosc_membrany(llenmidd, avarage_len ,test_freq, gora_dol)
        #obliczenia
        width = size[0]       
        self.szerokosc_membrany = ymembranaK - ymembranaP  #przyda sie do wyliczania odleglosci od membrany
        self.szerokosc_gornej_czesci_membrany = ymembrana- ymembranaP
        self.szerokosc_dolnej_czesci_membrany = ymembranaK - ymembrana
        #print "szerokosc gornej ",self.szerokosc_gornej_czesci_membrany, " szerokosc dolnej ",self.szerokosc_dolnej_czesci_membrany
        
        #tworze dwuwymiarowa tablice pozycji punktow prazkow
        lallmiddles_up = self.znajdz_gorne_prazki(gray, margin, ymembranaP, size, white_level, dark_level, test_freq)
        #tworze dwuwymiarowa tablice pozycji punktow prazkow
        lallmiddles_down = self.znajdz_dolne_prazki(gray, margin, ymembranaK, size, white_level, dark_level, test_freq)
        #szukam zgrubnie okresu - sredni okres prazkow na zdjeciu
        przyblizony_okres = self.znajdz_przyblizony_okres(avarage_len, size)

        diff = przyblizony_okres*mnoznik
        #print "srednia ilosc rzadkow" , avarage_len, "przyblizony okres" , przyblizony_okres
        
        #######################################    zajmuje sie gornymi prazkami #######################################
        self.lista_do_wyznaczania_zasiegu_dyfuzji=[]
        self.wyniki_gorne =[[],[]]
        if gora_dol[0]: #jesli wybrana gora to wykonuje ponizsze
            tablica_prazkow_up= [[0]*avarage_len]*len(lallmiddles_up)  #tworze tablice do przechowywania pozycji punktow prazkow
            if len(tablica_prazkow_up)>0:
                if len(tablica_prazkow_up[0])>1:
                    tablica_prazkow_up[0][1]=1
                
            lista_wszystkich_odleglosci_od_stycznej=[]
            for numer_prazka in range(1,avarage_len):  #iteruje po kazdym prazku

                tab_poczatkowych = self.znajdz_poczatek_prazka(lallmiddles_up, numer_prazka, quant_x0) # znajduje poczatkowe punkty prazka
                if len(tab_poczatkowych)<1:
				     continue
                prazek = self.przyporzadkuj_prazkowi_najblizszy_punkt(lallmiddles_up, numer_prazka, tab_poczatkowych, quant_x0, diff , size) # wyznaczam dalszy bieg prazka na podstawie poczatkowych punktow

                odcinki =self.wylicz_dynamiczna_styczna_do_prazka(prazek, punkty_na_styczna, quant_x0, test_freq, gray) # wylicza styczna dynamiczna
                self.lista_do_wyznaczania_zasiegu_dyfuzji.append(odcinki)
                
                #czytam po dwa odcinki, licze wsp kierunkowe, sr_wsp_kier = sr_wsp_kier + wsp_kier_odc/i  
                #gdzie i to liczba wszystkich dotychczasowych odcinkow
                #jesli wsp_kier_odc rozni sie o n% od sr_wsp_kier i poprzedni wsp_kier_odc tez sie roznil i przepoprzedni
                # to znaczy ze to juz jest zagiecie
                ilosc_odcinkow= len(odcinki)
                ilosc_wyznaczeniowa = int(ilosc_odcinkow*ulamek_koncowkowy)

                x_sr1, y_sr1, x_sr2, y_sr2 = self.wyznacz_dwa_punkty_do_aproksymacji_liniowej_prazka(odcinki, ilosc_wyznaczeniowa, 1)
                if (x_sr1 ==-1 or y_sr1==-1 or x_sr2==-1 or y_sr2==-1):
		            continue
                a= float(x_sr1 -x_sr2)/float(y_sr1-y_sr2)
                b = x_sr2 - a*y_sr2
                xmembrana = int(b+ a* ymembrana)
                #print "xmembrana" ,xmembrana , "a" ,a ,"b" ,b

                self.rysuj_aproksymacje_liniowa(x_sr1, y_sr1, x_sr2, y_sr2, xmembrana, ymembrana, gray, quant_x0 ) #rysuje styczna do prostoliniowego prazka
                odleglosci = self.wylicz_odelglosci_od_stycznej(prazek, punkty_na_styczna, test_freq, quant_x0, a ,b) # odleglosc od stycznej
                lista_wszystkich_odleglosci_od_stycznej.append(odleglosci)
                 
            #znajduje doklady okres, bo potrzebny jest do dalszych obliczen
            okres_gornych_prazkow = self.znajdz_dokladny_okres(tablica_prazkow_up, skala, size)
            #print "OKRES GORNYCH PRAZKOW!!!!!!!!!!" , okres_gornych_prazkow
            # delta_c =  a * d / (okres * f)
            #przygotowuje dane do wykresu
            lista_wartosci_do_wykresu_gornych, y_gorne=self.przygotuj_dane_do_wykresu(lista_wszystkich_odleglosci_od_stycznej
            ,quant_x0, test_freq, skala, okres_gornych_prazkow, a_gorne, f, dlugosc_fali,self.C_gorne,self.zasieg_dyfuzji_gora)
            self.wyniki_gorne = [lista_wartosci_do_wykresu_gornych, y_gorne]
            print "WYNIKI GORNE",  self.wyniki_gorne
            ##############  FUNKCJE DO WYZNACZENIA OBSZARU DYFUZJI
            #self.zasieg_dyfuzji_gora = self.wyznacz_zasieg_dyfuzji(self.lista_do_wyznaczania_zasiegu_dyfuzji, k_grad,1,skala) #wyznaczam zasieg dysuzji na podstawie kryt gradientowego
            #wyznaczam zasieg dysuzji na podstawie kryterium
            self.zasieg_dyfuzji_gora = self.wyznacz_zasieg_dyfuzji_2(self.wyniki_gorne, okres_gornych_prazkow,   k_grad, dlugosc_fali,  a_gorne, f,   rodzaj_kryterium)
            print self.zasieg_dyfuzji_gora
            #rysuje na wysokosci konca dyfuzji
            cv.Line(gray,(0,(ymembranaP - int(self.zasieg_dyfuzji_gora * skala))),(size[0],(ymembranaP - int(self.zasieg_dyfuzji_gora*skala))),(255,255,255),3)
            ########
            #licze ilosc substacncji ktora dyfundowala
            self.ilosc_substancji_gora = self.wylicz_ilosc_substancji(szerokosc_membrany, f, self.wyniki_gorne, self.zasieg_dyfuzji_gora)
            #licze strumien
            self.strumien_gora = self.wylicz_strumien(self.ilosc_substancji_gora, czas)
            #licze wsp dyfuzji na gornych prazkach
            self.wspolczynnik_dyfuzji_gora = self.wylicz_wspolczynnik_dyfuzji(self.zasieg_dyfuzji_gora, k_grad, czas)
             

        # ROBIE TO SAMO DLA DOLNYCH
        ######################################################################tera dolnymi ####################3 
        self.lista_do_wyznaczania_zasiegu_dyfuzji=[]     
        self.wyniki_dolne =[[],[]]
        if gora_dol[1]:
            tablica_prazkow_down= [[0]*avarage_len]*len(lallmiddles_down)
            if len(tablica_prazkow_down)>0:
                if len(tablica_prazkow_down[0])>1:
                    tablica_prazkow_down[0][1]=1
                
            lista_wszystkich_odleglosci_od_stycznej=[]
            for numer_prazka in range(1,avarage_len):

                tab_poczatkowych = self.znajdz_poczatek_prazka(lallmiddles_down, numer_prazka, quant_x0)
                if len(tab_poczatkowych)<1:
				    continue
                prazek = self.przyporzadkuj_prazkowi_najblizszy_punkt(lallmiddles_down, numer_prazka, tab_poczatkowych, quant_x0, diff , size)

                odcinki =self.wylicz_dynamiczna_styczna_do_prazka(prazek, punkty_na_styczna, quant_x0, test_freq, gray, -1)  
	  
                #czytam po dwa odcinki, licze wsp kierunkowe, sr_wsp_kier = sr_wsp_kier + wsp_kier_odc/i  
                #gdzie i to liczba wszystkich dotychczasowych odcinkow
                #jesli wsp_kier_odc rozni sie o n% od sr_wsp_kier i poprzedni wsp_kier_odc tez sie roznil i przepoprzedni
                # to znaczy ze to juz jest zagiecie
                self.lista_do_wyznaczania_zasiegu_dyfuzji.append(odcinki)
                
                ilosc_odcinkow= len(odcinki)
                ilosc_wyznaczeniowa = int(ilosc_odcinkow*ulamek_koncowkowy)
                x_sr1, y_sr1, x_sr2, y_sr2 = self.wyznacz_dwa_punkty_do_aproksymacji_liniowej_prazka(odcinki, ilosc_wyznaczeniowa, -1)
                if (x_sr1 ==-1 or y_sr1==-1 or x_sr2==-1 or y_sr2==-1):
		            continue
                a= float(x_sr1 -x_sr2)/float(y_sr1-y_sr2)
                b = x_sr2 - a*y_sr2
                xmembrana = int(b+ a* ymembrana)
                print "xmembrana" ,xmembrana , "a" ,a ,"b" ,b
                cv.Circle(gray,(x_sr1,y_sr1),4,(0,0,0),5)

                self.rysuj_aproksymacje_liniowa(x_sr1, y_sr1, x_sr2, y_sr2, xmembrana, ymembrana, gray, quant_x0 )
                odleglosci = self.wylicz_odelglosci_od_stycznej(prazek, punkty_na_styczna, test_freq, quant_x0, a ,b, -1, size)
                lista_wszystkich_odleglosci_od_stycznej.append(odleglosci)

       
            okres_dolnych_prazkow = self.znajdz_dokladny_okres(tablica_prazkow_down, skala, size)
            lista_wartosci_do_wykresu_dolne, y_dolne=self.przygotuj_dane_do_wykresu(lista_wszystkich_odleglosci_od_stycznej
            ,quant_x0, test_freq, skala, okres_dolnych_prazkow, a_dolne, f, dlugosc_fali,self.C_dolne,self.zasieg_dyfuzji_dol)

            self.wyniki_dolne = [lista_wartosci_do_wykresu_dolne, y_dolne]
            
            ############## TU ROBIE FUNKCJE DO WYZNACZENIA OBSZARU DYFUZJI
            self.zasieg_dyfuzji_dol = self.wyznacz_zasieg_dyfuzji_2(self.wyniki_dolne, okres_dolnych_prazkow,   k_grad, dlugosc_fali,  a_dolne, f, rodzaj_kryterium)
            print "ZASIEG DYFUZJI DOLNY  ", self.zasieg_dyfuzji_dol
            cv.Line(gray,(0,(ymembranaK + int(self.zasieg_dyfuzji_dol*skala))),(size[0],(ymembranaK + int(self.zasieg_dyfuzji_dol*skala))),(255,255,255),3)
            ##############################
            
            self.ilosc_substancji_dol = self.wylicz_ilosc_substancji(szerokosc_membrany, f, self.wyniki_dolne, self.zasieg_dyfuzji_dol)
            self.strumien_dol = self.wylicz_strumien(self.ilosc_substancji_dol,czas) 
            self.wspolczynnik_dyfuzji_dol = self.wylicz_wspolczynnik_dyfuzji(self.zasieg_dyfuzji_dol, k_grad, czas)      

        #rysuje to co zrobil algorytml
        if podglad:
            thread.start_new_thread(self.pokaz_podglad_dzaialania_algorytmu,(gray,))
########################################################################            
########################################################################  
        #liczy strumien          
    def wylicz_strumien(self, ilosc_substancji,czas):
        print "wylicz strumien"
        if czas>0.0000001:
            return ilosc_substancji/float(czas)*1000.0
        else:
            return ilosc_substancji * 100000
            
        #liczy ilosc substancji
    def wylicz_ilosc_substancji(self,dlugosc_membrany, szerokosc_membrany, wyniki ,zasieg):
        calka =0
        i=0 
        try:
            while (i<range(len(wyniki[0])) and wyniki[1][i]< zasieg):
			    calka = wyniki[0][i]+calka
			    i+=1
            return dlugosc_membrany*szerokosc_membrany*calka* wyniki[1][i]
        except:
			return 0
			
        #przygotowuje dane do wykresu - odleglosci od stycznej przeliczam na wspolczynniki C  
    def przygotuj_dane_do_wykresu(self, lista_wszystkich_odleglosci_od_stycznej, quant_x0, test_freq,skala,okres_prazkow,a,f, dlugosc_fali,C_0,zasieg_dyfuzji):      
        i=0
        max_dlugosc=0
        for pr in lista_wszystkich_odleglosci_od_stycznej:
            if i==0:
                max_dlugosc = len(pr)
            else:
                max_dlugosc = max(max_dlugosc, len(pr))
            i+=1
        y=[]
        lista_wartosci_do_wykresu =[]

        for num_rzadka in range(max_dlugosc):
            lista_odleglosci =[]
            for num_praz in range(len(lista_wszystkich_odleglosci_od_stycznej)):
                if len(lista_wszystkich_odleglosci_od_stycznej[num_praz])>num_rzadka:
                    lista_odleglosci.append(lista_wszystkich_odleglosci_od_stycznej[num_praz][num_rzadka])
            srednia_odleglosc = sum(lista_odleglosci)/len(lista_odleglosci)
            #yi = ((num_rzadka+quant_x0)*test_freq - self.szerokosc_membrany/2.0)/skala
            yi = ((num_rzadka)*test_freq - self.szerokosc_membrany/2.0)/skala
            #if yi < zasieg_dyfuzji:
                #print yi ,"  wieksze od  " ,zasieg_dyfuzji
            y.append(yi)
            lista_wartosci_do_wykresu.append(-(0.000001*dlugosc_fali)*a*(srednia_odleglosc/skala)/(okres_prazkow*f)+C_0) 
        #y.reverse()
        lista_wartosci_do_wykresu.reverse()
        return lista_wartosci_do_wykresu, y
            
        #wyswietla w nowym oknie podglad dzialania algorytmu
    def pokaz_podglad_dzaialania_algorytmu(self, gray):
        cv.NamedWindow("PODGLAD DZIALANIA ALGORYTMU", 1)
        cv.ShowImage("PODGLAD DZIALANIA ALGORYTMU",gray)
        cv.WaitKey(0)
     
        #przygotowuje zdjecie - proguje je itp
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
        
        # szuka ile jest gornych prazkow
    def znajdz_ilosc_gornych_prazkow(self, size, test_freq, gray, white_level, dark_level, margin):
        ly=[]      # do tego zapisuje caly rzadek 
        lblack= [] # do tego zapisuje polozenie pikseli <10 a potem kasuje jak juz policze srodek prazka
        lmiddle=[] # do tego zapisuje polozenie srodkow kolejnych prazkow
        llenmidd=[]
        lallmiddles=[]

        j=0
        for py in range(size[1]):  #idzie od gory do dolu
            if py%test_freq==0:
                k=0
                l=0
                for px in range(size[0]): #idzie od lewej do prawej
                    l+=1
                    ly.append(gray[py,px])
                    if gray[py,px]>white_level and px>margin and px < size[0]-margin: #jezeli cos jest ciemne i nie lezy po bokach
                        lblack.append(px)
                    
                    if (gray[py,px]<dark_level and gray[py,px-1]<dark_level):  #jezeli 3 piksele obok siebie sa biale
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
        return avarage_len, llenmidd ,lallmiddles

        #szuka wysokosci membrany, zwraca wysokosc membrany
    def znajdz_wysokosc_membrany(self, llenmidd, avarage_len, test_freq,gora_dol):
        lymembrana=[]
        i=0
        print "WYBRALES PRAZKI " ,gora_dol
        for lenmiddle in llenmidd:
            if lenmiddle < avarage_len*0.1 :
		        lymembrana.append(test_freq*i)
            i+=1
        if len(lymembrana)<1:
            if gora_dol[0]:
                ymembrana, ymembranaP ,ymembranaK = test_freq*i,test_freq*i,test_freq*i
            elif gora_dol[1] and not gora_dol[0]:
                ymembrana, ymembranaP ,ymembranaK = 0,0,0
            print "nie ma membrany"
        else:
            ymembrana = sum(lymembrana)/len(lymembrana)
            ymembranaP = lymembrana[0]
            ymembranaK = lymembrana.pop()

        return ymembrana, ymembranaP ,ymembranaK
        
	    # znajduje najblizszy punkt i zwraca jego indeks i odleglosc od 'wartosc'
    def closest_point_index(self, array, wartosc, diff):
        i=0
        index=0
        #print "ilosc prazkow" , len(array), "value", wartosc
        for element in array:
            roznica = wartosc - element
            if roznica<0:
			    roznica=roznica*(-1)
            #print "diff",roznica
            if i==0:
			    diff_min=diff
        
            if roznica<diff_min:
                diff_min=roznica
                index = i
                #print "najmniejsza roznica",roznica
            i+=1
        return index,diff_min
        
		#znajduje gorne prazki
    def znajdz_gorne_prazki(self, gray, margin, ymembranaP, size, white_level, dark_level, test_freq):
        # ze ide od gory do mebrany
        # a potem od dolu do membrany
        lblack= [] # do tego zapisuje polozenie pikseli <10 a potem kasuje jak juz policze srodek prazka
        lmiddle=[] # do tego zapisuje polozenie srodkow kolejnych prazkow
        llenmidd=[]
        lallmiddles_up=[]

        # GORNE PRAZKI
        j=0
        for py in range(margin/2,ymembranaP):    # badam zdjecie od gornej krawedzi minus margines do membrany (lub konca zdjecia)
            if py%test_freq==0:
                k=0
                l=0
                for px in range(size[0]): # lece od lewej do prawej
                    l+=1
                    #ly.append(gray[py,px])
                    if gray[py,px]>white_level and px>margin and px < size[0]-margin: #jezeli cos jest ciemne i nie lezy po bokach
                        lblack.append(px)
                    if 1: # sprawdza czy nie jest na poczatku zdjecia
                        if (gray[py,px]<dark_level and gray[py,px-1]<dark_level ):  #jezeli 2 piksele obok siebie sa biale
                            if len(lblack)>3:  
					            # zakladam ,ze prazek nie moze byc cienszy od 4 pix (2 to minimum, bo inaczej nie policze sredniej)
                                pxsrednie = lblack[len(lblack)/2]
                                lmiddle.append(pxsrednie)
                                k+=1  # k liczy ilosc zanotowanych srodkow prazka (ilosc prazkw)
                                #cv.Circle(gray,(pxsrednie,py),2,(170,0,0),2)	
                                lblack=[]    
                j+=1 # MOWI W KTORYM JESTESMY RZADKU
                llenmidd.append(len(lmiddle))
                # print len(lmiddle)
                lallmiddles_up.append(lmiddle)
                lmiddle=[]
        return lallmiddles_up
        
        # znajduje dolne prazki, zwraca tablice srodkow prazkow - nie posegregowanych na prazki
    def znajdz_dolne_prazki(self, gray, margin, ymembranaK, size, white_level, dark_level, test_freq):

        # DOLNE PRAZKI  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        przedzial = range(ymembranaK, size[1]-margin/2)
        przedzial.reverse()
        lallmiddles_down=[]
        llenmidd=[]
        lblack=[]
        lmiddle=[]
        j=0
        for py in przedzial:  
            if py%test_freq==0:
                k=0
                l=0
                for px in range(size[0]):
                    l+=1
                    #ly.append(gray[py,px])
                    if gray[py,px]>white_level and px>margin and px < size[0]-margin: #jezeli cos jest ciemne i nie lezy po bokach
                        lblack.append(px)
                    if 1: # sprawdza czy nie jest na poczatku zdjecia
                        if (gray[py,px]<dark_level and gray[py,px-1]<dark_level):  #jezeli 3 piksele obok siebie sa biale
                            if len(lblack)>3:  
					            # zakladam ,ze prazek nie moze byc cienszy od 4 pix (2 to minimum, bo inaczej nie policze sredniej)
                                #pxsrednie = sum(lblack)/len(lblack)
                                pxsrednie = lblack[len(lblack)/2]
                                lmiddle.append(pxsrednie)
                                k+=1  # k liczy ilosc zanotowanych srodkow prazka (ilosc prazkw)
                                #cv.Circle(gray,(pxsrednie,py),2,(168,0,0),2)	
                                lblack=[]    
                j+=1 # MOWI W KTORYM JESTESMY RZADKU
                llenmidd.append(len(lmiddle))
                #print len(lmiddle)
                lallmiddles_down.append(lmiddle)
                lmiddle=[]
        return lallmiddles_down

        #znajduje z grubsza wyliczony (sredni ) okres prazkow
    def znajdz_przyblizony_okres(self, avarage_len, size):
        if avarage_len>0:
            return size[0]/avarage_len
        else:
            return size[0]*2

        # znajduje dokladny okres prazkow - wczytuje liste juz posegregowanych prazkow
    def znajdz_dokladny_okres(self, lista_prazkow , skala , size):
        print "znajdz dokladny okres"
        suma_rzadkow = 0
        for rzad in lista_prazkow:
            suma_rzadkow += len(rzad)
        dlugosc =len(lista_prazkow)
        if dlugosc >0:
            srednia_ilosc_rzadkow = suma_rzadkow/dlugosc
            if srednia_ilosc_rzadkow > 0 and skala >0:
                okres = size[0]/srednia_ilosc_rzadkow/skala
                return okres
        else:
			return size[0]*2			
		
    #funkcja szuka punktow ktore sa najblizej - tzn pochodza od tego samego prazka
    #funkcja uzywa algorytmow z teorii grup - najblizsza srednia
    def przyporzadkuj_prazkowi_najblizszy_punkt(self, lallmiddles_up, numer_prazka, tab_poczatkowych, quant_x0, diff, size):
        tab_poczatkowych=sorted(tab_poczatkowych)
        #print tab_poczatkowych , " - tab poczatkowych"
        mediana = tab_poczatkowych[len(tab_poczatkowych)/2]
        #print "mediana" ,len(tab_poczatkowych) ,"poczatkowych pynktow prazka nr. ",numer_prazka," to", mediana  

        prazek=[]
        j=0
        for rzad in lallmiddles_up:  #biore rzad zawierajacy po jednym punkcie z kazdego prazka
            if len(rzad)>numer_prazka:  # jesli ilosc prazkow jest wieksza od wybranego numeru prazka to mozesz kontynuowac 
                if j==quant_x0:
			        #lallmiddles_up[j-1][numer_prazka]=mediana # ostatni punkt poczatku prazka robie rowny medianie punktow sprawdzajacych poczatek
			        prazek.append(mediana)  
			    # Jesli juz przejde przez pkt poczatkowe to analizuje dlaszy bieg prazka
                elif j>quant_x0 and len(lallmiddles_up[j-1])>numer_prazka and len(prazek)>0: 
                    index,r = self.closest_point_index(rzad,prazek[len(prazek)-1], diff) # zwraca w ktorym prazku byl najblizszy
                    polozenie = rzad[index]
                    if r<diff:
                        prazek.append(polozenie)
                        if polozenie >= (size[0]-1) or polozenie <2:
							break
                    else: # jesli najblizszy punkt jest daleko, to znaczy ,ze jest dziura w prazku i nalezy zaproksymowac polozenie nastepnego
                        if len(prazek)>4:
                            d1= prazek[len(prazek)-1]-prazek[len(prazek)-2]  # aproksymuje polozenie liczac zmiane odleglosci poprzednich punktow
                            d2= prazek[len(prazek)-2]-prazek[len(prazek)-3]
                            d3= prazek[len(prazek)-3]-prazek[len(prazek)-4]                    
                            d4= prazek[len(prazek)-4]-prazek[len(prazek)-5]                    
                            #d = (d4+ d3+ d2+ d1)/4   
                            d = (d4+ d3+ d2+ d1)/3
                            #if abs(df -d) >0.5:
							#	d=int(2*df - d) # powiekszam bo dzielenie przez int zaniza wynik (zaokragal w dol)
                            polozenie = prazek[len(prazek)-1]+d	
                            prazek.append(polozenie)
                            if polozenie >= (size[0]-1) or polozenie <2:
							    break
                    
            j+=1
        #print "prazek skladal sie z tylu pkt:  " , len(prazek)
        return prazek
        
        # znajduje poczatkowe punkty prazkow
    def znajdz_poczatek_prazka(self, lallmiddles_up, numer_prazka,quant_x0):
        j=0
        tab_poczatkowych =[]
        for rzad in lallmiddles_up:
            if len(rzad)>numer_prazka:  # jesli ilosc srodkow prazka jest wieksza od wybranego numeru prazka to mozesz kontynuowac 
                tab_poczatkowych.append(rzad[numer_prazka])
                if j>quant_x0:
                    break
            j+=1
        return tab_poczatkowych
        
        #wylicza ta styczna ktora kroczy dokladnie po prazku
    def wylicz_dynamiczna_styczna_do_prazka(self, prazek, punkty_na_styczna, quant_x0, test_freq, gray, gora_czy_dol=1):
        konce_stycznej=[]
        odcinki=[]
        j=0
        line_ends=[[0,0],[0,0]]  # odcinek styczny miesjcowo do prazka
        ilosc_odcinkow=len(prazek)/punkty_na_styczna
        height = cv.GetSize(gray)[1]
        if gora_czy_dol==-1: # dla dolnych prazkow
            for i in range(ilosc_odcinkow):
                if i==0:
                    line_ends[0][0]=prazek[i*punkty_na_styczna]
                    line_ends[0][1]=height - (i*punkty_na_styczna+quant_x0)*test_freq
                else:
                    line_ends[1][0]=prazek[i*punkty_na_styczna]
                    line_ends[1][1]=height - (i*punkty_na_styczna+quant_x0)*test_freq
                    odcinki.append(line_ends)
                    cv.Line(gray,(line_ends[0][0],line_ends[0][1]),(line_ends[1][0],line_ends[1][1]),(210,0,0),2)
                    line_ends=[[0,0],[0,0]]
                    line_ends[0][0]=prazek[i*punkty_na_styczna]
                    line_ends[0][1]=height - (i*punkty_na_styczna+quant_x0)*test_freq
                    
        else:  # dla gornych prazkow
            for i in range(ilosc_odcinkow):
                if i==0:
                    line_ends[0][0]=prazek[i*punkty_na_styczna]
                    line_ends[0][1]=(i*punkty_na_styczna+quant_x0)*test_freq
                else:
                    line_ends[1][0]=prazek[i*punkty_na_styczna]
                    line_ends[1][1]=(i*punkty_na_styczna+quant_x0)*test_freq
                    odcinki.append(line_ends)
                    cv.Line(gray,(line_ends[0][0],line_ends[0][1]),(line_ends[1][0],line_ends[1][1]),(210,0,0),2)
                    line_ends=[[0,0],[0,0]]
                    line_ends[0][0]=prazek[i*punkty_na_styczna]
                    line_ends[0][1]=(i*punkty_na_styczna+quant_x0)*test_freq
        return odcinki

        #wyznacza 2 punkty na prazku ktore sluza do narysowania prostoliniowej stycznej
    def wyznacz_dwa_punkty_do_aproksymacji_liniowej_prazka(self, odcinki,ilosc_wyznaczeniowa,gora_czy_dol):
        #a_sr=0
        sum_x=0
        sum_y=0
        sum_a=0
        x_sr1, y_sr1, x_sr2, y_sr2 =-1,-1,-1,-1
        i=0
        for i in range(ilosc_wyznaczeniowa/3):
            if i>0:
                dx= (odcinki[i][0][0]-odcinki[i][1][0])
                dy= (odcinki[i][0][1]-odcinki[i][1][1])
                sum_x +=odcinki[i][0][0]
                sum_y +=odcinki[i][0][1]
        if i>0:
            x_sr1= sum_x/i
            y_sr1= sum_y/i

        sum_x=0
        sum_y=0
        for i in range(ilosc_wyznaczeniowa/3, ilosc_wyznaczeniowa):
            if i>0:
                dx= (odcinki[i][0][0]-odcinki[i][1][0])
                dy= (odcinki[i][0][1]-odcinki[i][1][1])
                sum_x +=odcinki[i][0][0]
                sum_y +=odcinki[i][0][1]
        if i>0:	
            x_sr2= sum_x/(ilosc_wyznaczeniowa- ilosc_wyznaczeniowa/3)
            y_sr2= sum_y/(ilosc_wyznaczeniowa- ilosc_wyznaczeniowa/3)
        return x_sr1, y_sr1, x_sr2, y_sr2
         
        # liczy odleglosc od stycznej - zwraca tablice odleglosci od stycznej   
    def wylicz_odelglosci_od_stycznej(self, prazek, punkty_na_styczna, test_freq ,quant_x0, a ,b,gora_czy_dol=1 , size=[0,0]):
        odleglosci =[]
        y=[]
        i=0
        if gora_czy_dol ==1:
            for x in prazek:
                yi = (i*punkty_na_styczna+quant_x0)*test_freq #-self.szerokosc_gornej_czesci_membrany
                y.append(yi)
                x_stycz = int(b+a*yi)
                odleglosci.append(x_stycz-x) 
                i+=1
        else:
            for x in prazek:
                yi = size[1] - (i*punkty_na_styczna+quant_x0)*test_freq #- self.szerokosc_dolnej_czesci_membrany
                y.append(yi)
                x_stycz = int(b+a*yi)
                odleglosci.append(x_stycz-x) 
                i+=1
        return odleglosci

        #rysuje aproksymacje liniowa prostoliniowego prazka
    def rysuj_aproksymacje_liniowa(self, x_sr1, y_sr1, x_sr2, y_sr2,xmembrana, ymembrana,gray,quant_x0,gora_czy_dol=1):
        #print x_sr1, x_sr2, y_sr1, y_sr2
        #print xmembrana,ymembrana
        kolor =160
        srednica =2
        if gora_czy_dol==-1:
			kolor = 230
			srednica =5
        cv.Circle(gray,(x_sr1,y_sr1),4,(128,0,0),srednica)
        cv.Circle(gray,(x_sr2,y_sr2),4,(128,0,0),srednica)
        cv.Circle(gray,(xmembrana,ymembrana),4,(255,0,0),srednica)
        cv.Line(gray,(xmembrana,ymembrana),(x_sr1,y_sr1),(kolor,0,0),3)

        #przygotowyje string do zapisu w pliku
    def daj_string_z_wynikami(self, komentarz=""):
		print "daj string z wynikami"
		string_wynikowy = "Photo:  " + self.url +"\n"
		string_wynikowy += "Data: " + time.asctime( time.localtime(time.time()) ) + "\n"
		string_wynikowy += "Comment: " + komentarz +"\n"
		string_wynikowy += "Upper fringes - CONCENTRATION C\n" 
		string_wynikowy += "Diffusion range: "  + str(self.zasieg_dyfuzji_gora) + "  Subst. ammount: "+str(self.ilosc_substancji_gora)+"  Flow: "+str(self.strumien_gora)+ " Diffusion coefficient: " +str(self.wspolczynnik_dyfuzji_gora)+"\n"
		string_wynikowy += "x[mm]" +"\t" +"\t"+ "Value \n"
		for i in range(len(self.wyniki_gorne[0])):
			string_wynikowy += str(self.wyniki_gorne[1][i]).zfill(11) +"\t"+ str(self.wyniki_gorne[0][i]) +"\n"
		
		string_wynikowy += "\n"
		
		string_wynikowy += "Down fringes - CONCENTRATION C\n"
		string_wynikowy += "Diffusion range: "  + str(self.zasieg_dyfuzji_dol) +  "  Subst. ammount: "+str(self.ilosc_substancji_dol)+"  Flow: "+str(self.strumien_dol)+ " Diffusion coefficient: " +str(self.wspolczynnik_dyfuzji_dol)+"\n"
		string_wynikowy += "x[mm]" +"\t" +"\t"+ "Value \n"
		for i in range(len(self.wyniki_dolne[0])):
			string_wynikowy += str(self.wyniki_dolne[1][i]).zfill(11) +"\t"+ str(self.wyniki_dolne[0][i]) +"\n"	

		return string_wynikowy
        
        # eksportuje przygotowany string do pliku
    def eksportuj_do_pliku_txt(self,string_z_wynikami):
		print "eksportuje do pliku txt"
		txt_file_url = self.url.rsplit(".",2)[0] +".txt"
		txt_file = open(txt_file_url,"w")
		txt_file.write(string_z_wynikami)
		txt_file.close()	

        #wylicza wspolczynnik dyfuzji
    def wylicz_wspolczynnik_dyfuzji(self, zasieg_dyfuzji, kryterium_stezeniowe, czas):
        print "wylicz wspolczynnik dyfuzji"
        mianownik =float(4*czas*(1-math.erf(kryterium_stezeniowe)))
        if mianownik==0:
            mianownik =0.00000000001
        D = zasieg_dyfuzji**2 / mianownik
        return D
		
		#wyznacza zasieg dyfuzji
    def wyznacz_zasieg_dyfuzji(self,lista_stycznych, k_grad,gora_czy_dol,skala, rodzaj_kryterium=0):
        print "wyznacz zasieg dyfuzji" , "WARTOSC GRANICZNA" , k_grad
        zasieg=0
        #print "LISTA STYCZNYCH" ,  lista_stycznych
        if rodzaj_kryterium==0:
            lista_wysokosci = []
            # self.lista_do_wyznaczania_zasiegu_dyfuzji ma postac :  [line_ends1, line_ends2...] gdzie line_ends=[[x11,y11],[x12,y12]]
            # wsp kierunkowy to  (x12 -x11)/(y12 - y11)
            dzielnik = k_grad
            if gora_czy_dol:
                if k_grad>0:
                    k_grad=float(1.0/dzielnik)
                else:
                    k_grad=45.0
            for styczne_prazka in lista_stycznych:
                for i in range(len(styczne_prazka)):
                    wsp_kier = abs(float(styczne_prazka[i][1][0] - styczne_prazka[i][0][0])/float(styczne_prazka[i][1][1] - styczne_prazka[i][0][1]))
                    if wsp_kier>k_grad:
                        lista_wysokosci.append(styczne_prazka[i][0][1])
                        break
            print "lista wysokosci to   ",lista_wysokosci
            if len(lista_wysokosci)>0:
                zasieg = sum(lista_wysokosci)/len(lista_wysokosci)
                print "wysokosc to", zasieg
            else:
                zasieg = 0
        return float(zasieg/skala)
        
    def wyznacz_zasieg_dyfuzji_2(self,  wyniki, okres_prazkow,   kryterium, dlugosc_fali,  a, f,   rodzaj_kryterium):
        wartosci = wyniki[0]
        polozenie = wyniki[1]
        if(rodzaj_kryterium ==0):
            print "kryterium gradientowe"
            for i in range(len(wartosci)):
                if i >0: 
                    nachylenie = abs((wartosci[i]-wartosci[i-1])/(polozenie[i]-polozenie[i-1]))
                    print "nachylenie ", nachylenie , "kryterium ", kryterium
                    if kryterium < nachylenie :
                        print "graniczne nachylenie wynosi ",  nachylenie
                        return polozenie[i]
        elif(rodzaj_kryterium ==1):
            print "kryterium stezeniowe"
            maksymalna_wartosc = max(wartosci)
            minimalna_wartosc = min(wartosci)
            if abs(minimalna_wartosc) > maksymalna_wartosc:
				maksymalna_wartosc = abs(minimalna_wartosc)
            graniczna_wartosc = abs(float(kryterium)/100.0*maksymalna_wartosc)
            for i in range(len(wartosci)):
                if abs(wartosci[i])<graniczna_wartosc:
                    print "GRANICZNA WARTOSC ",  graniczna_wartosc ,  wartosci[i] ,  polozenie[i], "maksymalna " , maksymalna_wartosc
                    return polozenie[i]
        elif(rodzaj_kryterium ==2):
            print "kryterium prazkowe"
            graniczne_odchylenie = (0.000001*dlugosc_fali*a*kryterium*(okres_prazkow/2.0)/(okres_prazkow*f))
            for i in range(len(wartosci)):
                if abs(wartosci[i])<graniczne_odchylenie:
                    return polozenie[i]
        return 0
            
        
        # znajduje jaka wartosc ma wsp C na zadanej wysokosci - czyta plik z wynikami
    def znajdz_wartosc_w_tekstowym_na_wysokosci(self,url,gora_dol,wysokosc):
        f=open(url)
        print url , gora_dol, wysokosc
        lista_wartosci=[]
        active_note=0
        i=-1
        for line in f:
            i+=1
            if i==1:
                continue          
            if gora_dol[0]:
                 if line.rfind("Upper")!=-1:
                    active_note=1
                    i=0
            else:
                 if line.rfind("Down")!=-1:
                    active_note=2
                    print "znalazlem"
                    i=0                   
            if i>2 and active_note==1:
                if line.find("Down")!=-1:
                    break
                if len(line.split("\t"))>1:				
                    lista_wartosci.append( [line.split("\t")[0].strip(),line.split("\t")[1].strip()] )
                    print line, "dodale do gornych"
            elif i>2 and active_note==2:
                if len(line.split("\t"))>1:
                    lista_wartosci.append([line.split("\t")[0].strip(),line.split("\t")[1].strip()])
                    print line , "dodalem do dolnych"   
        f.close()
        if len(lista_wartosci)>0:
            minindex=0	
            for i in range(len(lista_wartosci)):
                if i==0:
                    minimum= abs(eval(lista_wartosci[0][0])-wysokosc)
                    minindex=i
                else:
                    if abs(eval(lista_wartosci[i][0])-wysokosc) < minimum:
                        minindex=i	    			    				    
            wartosc_na_wysokosci=lista_wartosci[minindex][1]
            return wartosc_na_wysokosci
        else:
			return "0.0"
				
				    
				    
			
