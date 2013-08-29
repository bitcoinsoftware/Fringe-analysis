import cv
import thread

class Skalownik:
    def __init__(self, ROI, url):
        print "tworze skalownik"
        src = url
        test_freq =1
        margin =0
        dark_level=64
        white_level=120
        punkty_na_styczna = 4
        quant_x0=10 # wieksze od 2 mowi ile pkt poczatkowych biore do wyznaczenia pozycji prazka
        ulamek_koncowkowy =0.5
        #TOLERANCJA
        mnoznik=0.3
        gray , size = self.przygotuj_zdjecie(src, ROI, white_level, dark_level)
        self.srednica = self.znajdz_kolo(size, test_freq, gray, white_level, dark_level, margin)

        #rysuje to co zrobil algorytm
        thread.start_new_thread(self.pokaz_podglad_dzaialania_algorytmu,(gray,))

   
    def przygotuj_zdjecie(self, src, ROI,white_level, dark_level):
        img = cv.LoadImageM(src,cv.CV_LOAD_IMAGE_COLOR)
        size = cv.GetSize(img)
        print size
        gray = cv.CreateImage(size, 8, 1)
        cv.CvtColor(img, gray, cv.CV_RGB2GRAY)
        print ROI
        if ROI != [-1,-1,-1,-1]:
            cv.SetImageROI(gray, (ROI[0],ROI[1],ROI[2],ROI[3]))
        cv.Threshold(gray,gray, white_level, 255, cv.CV_THRESH_BINARY)
        cv.Smooth(gray,gray,cv.CV_BLUR,9,9)
        cv.Threshold(gray,gray, white_level*0.8, 255, cv.CV_THRESH_BINARY)
        cv.Smooth(gray,gray,cv.CV_BLUR,5,5)
        #cv.Dilate(gray,gray)
        #cv.Canny( gray, gray, 1.0, 1.0, 3)
        size = cv.GetSize(gray)
        return gray , size
  

    def znajdz_kolo(self, size, test_freq,gray, w_l, b_l, margin):
        ly=[]      # do tego zapisuje caly rzadek 
        lblack= [] # do tego zapisuje polozenie pikseli <10 a potem kasuje jak juz policze srodek prazka
        lmiddle=[] # do tego zapisuje polozenie srodkow kolejnych prazkow
        llenmidd=[]
        lallmiddles=[]
        #cv.Circle(gray,(pxsrednie,py),2,(128,0,0),2)
        #j=0
        g= 6
        print size , cv.GetSize(gray)
        l_x=[]
        for px in range(size[0]):  
            if px%test_freq==0:
                i=0
                for py in range(size[1]):
                    if gray[py,px] < b_l:
                        i+=1
            if i> 0.95 *size[1]:
                l_x.append(px)
                #cv.Line(gray,(px,0),(px,py),(210,0,0),2)
        if len(l_x)>0:
            srednie_x = sum(l_x)/len(l_x)
            #cv.Line(gray,(srednie_x,0),(srednie_x,py),(120,0,0),2)
        
            x_mniejsze = 0
            x_wieksze = size[0]
            for x in l_x:
			    if x < srednie_x:
				    x_mniejsze = x
			    elif x > srednie_x and x < x_wieksze:
				    x_wieksze = x
        
            cv.Line(gray, (x_mniejsze,int(size[1]*0.1)), (x_wieksze,int(size[1]*0.1)),(128,0,0),2)
            return (x_wieksze - x_mniejsze)
        else:
			return size[0]*2
				
    def get_diameter(self):
		return self.srednica      

    def pokaz_podglad_dzaialania_algorytmu(self, gray):
        cv.NamedWindow("PODGLAD DZIALANIA ALGORYTMU", 1)
        cv.ShowImage("PODGLAD DZIALANIA ALGORYTMU",gray)
        cv.WaitKey(0)
  
