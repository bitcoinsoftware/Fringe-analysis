from PyQt4 import QtGui,  QtCore

class QGraphicsScene2(QtGui.QGraphicsScene):
    def __init__(self,status, parent=None,TODO_pointer=None):
        self.status = status   # decyduje czy robic kolka czy kwadraty
        self.TODO = TODO_pointer
        super(QGraphicsScene2, self).__init__(parent)
        
    def set_display_widget(self, display, heigth, width):
        self.ROI = [-1,-1,-1,-1]
        self.heigth = heigth 
        self.width=width
        self.display = display
        self.pointsx=[]
        self.pointsy=[]
        self.x_move=0
        self.y_move=0
        self.skala_zdjecia=1.0
	
    def mouseReleaseEvent(self, event):
        button = event.button()
        #if self.active_listwidget=1:
        sk = self.skala_zdjecia
        if button == 1 and not self.status:
            point = self.display.mapFromGlobal(QtGui.QCursor.pos())
            print 'SIMPLE LEFT CLICK' , self.display.pos()
            self.pointsx.append((point.x()-self.x_move)) 
            self.pointsy.append((point.y()-self.y_move))
            #rysowanie kolek na granicach zaznaczenia
            self.addEllipse(point.x()-self.x_move,point.y()-self.y_move,6,6, QtCore.Qt.blue, QtGui.QBrush(QtCore.Qt.red))

            if len(self.pointsx)==2:
                self.pointsx=sorted(self.pointsx)
                self.pointsy=sorted(self.pointsy)
                rect_width = abs(self.pointsx[0]-self.pointsx[1])
                rect_heigth = abs(self.pointsy[0]-self.pointsy[1])
                self.addRect(self.pointsx[0],self.pointsy[0],rect_width, rect_heigth, QtCore.Qt.blue)
                
                self.ROI = [int(self.pointsx[0]/sk),int(self.pointsy[0]/sk),int(rect_width/sk), int(rect_heigth/sk)]
                i=0
                for wsp in self.ROI:
                    if self.ROI[i] <0:
                        self.ROI[i] =0
                    i=i+1
               
                if (self.ROI[0]+self.ROI[2]) > self.width:
                    self.ROI[2]=self.width-self.ROI[0]
                if (self.ROI[1]+self.ROI[3]) > self.heigth:
                    self.ROI[3] = self.heigth - self.ROI[1]
                print self.ROI
                
            if len(self.pointsx)==3:
                item_list=self.items()
                ilosc_obiektow = len(item_list)
                for i in range(ilosc_obiektow-2):
                    self.removeItem(self.items().pop(1))
                tempx=self.pointsx[2]
                tempy=self.pointsy[2]
                self.pointsx=[]
                self.pointsy=[]
                self.pointsx.append(tempx)
                self.pointsy.append(tempy)
                
        if button == 1 and self.status:  # jak zaznaczony radiobutt imbalance i subwidget aktywna
			point = self.display.mapFromGlobal(QtGui.QCursor.pos())
			self.addEllipse(point.x()-self.x_move,point.y()-self.y_move,6,6, QtCore.Qt.blue, QtGui.QBrush(QtCore.Qt.blue))
			#przekazuje wskaznik do funkcji i wywoluje ja z argumentami (point.x()-self.x_move,point.y()-self.y_move)
			self.TODO((point.x()-self.x_move),(point.y()-self.y_move))
	
    def mousePressEvent(self, event):
        button = event.button()
        if button == 1:
            print 'LEFT CLICK - DRAG'
        if button == 2:
            print 'RIGHT CLICK'
            item_list=self.items()
            ilosc_obiektow = len(item_list)
            for i in range(ilosc_obiektow-1):
                self.removeItem(self.items().pop(0))
            self.pointsx=[]
            self.pointsy=[]
