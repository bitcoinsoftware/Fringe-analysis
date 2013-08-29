from PyQt4 import QtCore, QtGui
from GuiFunctions import *
from PyQt4.phonon import Phonon
import os
import thread
from FolderWithItems import *
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class GuiConnections(GuiFunctions):
    size = [50,50]
    

    def connections(self):
		#buttons on the right
        QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL('clicked()'),self.turn_camera_on)
        QtCore.QObject.connect(self.pushButton_12,QtCore.SIGNAL('clicked()'),self.open_workspace)
        
        # photo buttons
        QtCore.QObject.connect(self.pushButton_3,QtCore.SIGNAL('clicked()'),self.item_analysis)  
        QtCore.QObject.connect(self.pushButton_6,QtCore.SIGNAL('clicked()'),self.scale)
        QtCore.QObject.connect(self.pushButton_15,QtCore.SIGNAL('clicked()'),self.save_scale)
        QtCore.QObject.connect(self.pushButton_7,QtCore.SIGNAL('clicked()'),self.add_to_sublist)
            
        #photo list widget
        QtCore.QObject.connect(self.pushButton_13,QtCore.SIGNAL('clicked()'),self.delete_photo)    
        QtCore.QObject.connect(self.listWidget,QtCore.SIGNAL('currentRowChanged(int)'),self.display_photo)
        QtCore.QObject.connect(self.listWidget,QtCore.SIGNAL('itemClicked(QListWidgetItem*)'),self.display_photo)

        
        #sub list
        QtCore.QObject.connect(self.listWidget_3,QtCore.SIGNAL('currentRowChanged(int)'),self.display_sublist_photo) 
        QtCore.QObject.connect(self.listWidget_3,QtCore.SIGNAL('itemClicked(QListWidgetItem*)'),self.display_sublist_photo)
        QtCore.QObject.connect(self.pushButton_11,QtCore.SIGNAL('clicked()'),self.clear_photo_sublist) 
        QtCore.QObject.connect(self.pushButton_14,QtCore.SIGNAL('clicked()'),self.add_all_to_photo_sublist)
        QtCore.QObject.connect(self.pushButton_9,QtCore.SIGNAL('clicked()'),self.remove_from_sublist) 
        QtCore.QObject.connect(self.pushButton_8,QtCore.SIGNAL('clicked()'),self.save_subresults) 
        QtCore.QObject.connect(self.pushButton_10,QtCore.SIGNAL('clicked()'),self.clear_subresults) 
        QtCore.QObject.connect(self.pushButton_2,QtCore.SIGNAL('clicked()'),self.time_item_analysis) 
        
        # Criterion frame
        QtCore.QObject.connect(self.radioButton_5,QtCore.SIGNAL('released()'),self.set_criterion_value)
        QtCore.QObject.connect(self.radioButton_6,QtCore.SIGNAL('released()'),self.set_criterion_value)
        QtCore.QObject.connect(self.radioButton_7,QtCore.SIGNAL('released()'),self.set_criterion_value)
        
         
           
            
        QtCore.QObject.connect(self.listWidget_2,QtCore.SIGNAL('currentRowChanged(int)'),self.display_video_info)
        #video list widget    
        QtCore.QObject.connect(self.pushButton_4,QtCore.SIGNAL('clicked()'),self.delete_video)
        QtCore.QObject.connect(self.pushButton_5,QtCore.SIGNAL('clicked()'),self.make_frames_from_video)
        #label menu        
        QtCore.QObject.connect(self.actionLoad_pictures,QtCore.SIGNAL('triggered()'),self.load_pictures)
        QtCore.QObject.connect(self.actionLoad_video_file,QtCore.SIGNAL('triggered()'),self.load_video)
        QtCore.QObject.connect(self.actionRemove_all_photos,QtCore.SIGNAL('triggered()'),self.remove_all_photos)
        QtCore.QObject.connect(self.actionRemove_all_videos,QtCore.SIGNAL('triggered()'),self.remove_all_videos)
        
        QtCore.QObject.connect(self.actionExit,QtCore.SIGNAL('triggered()'),self.exit_program)
          
  
        qsize = QtCore.QSize(self.size[0],self.size[1])
        self.listWidget.setIconSize(qsize)
        self.listWidget_2.setIconSize(qsize)
        self.skala= 60.0
        self.zczytaj_skale()
        self.doubleSpinBox_9.setValue(self.skala)
        #tekst = "Scale :   "+ str(self.skala)+" [ pix / mm]"
        #self.label_3.setText(QtGui.QApplication.translate("MainWindow", tekst, None, QtGui.QApplication.UnicodeUTF8))
        
        #self.add_existing_files()
        self.set_video_player()
    
    def zczytaj_skale(self):
        try:
            file = open("config.txt")
            for line in file:
                if line.find("skala")!=-1:
                    self.skala = eval(line.split("=")[1])
        except:
            print "coud not open config.txt file"


    def set_video_player(self): 
         
        self.mediaObject = Phonon.MediaObject(self.tab_2)
        self.videoWidget = Phonon.VideoWidget(self.tab_2)
        self.videoWidget.setGeometry(QtCore.QRect(199, 0, 641, 461))
        self.videoWidget.setObjectName(_fromUtf8("videoPlayer"))
        
        Phonon.createPath(self.mediaObject, self.videoWidget) 
        self.audioOutput = Phonon.AudioOutput(Phonon.VideoCategory, self.tab_2)
        Phonon.createPath(self.mediaObject, self.audioOutput)  

        self.metaInformationResolver = Phonon.MediaObject(self.tab_2)
        self.mediaObject.setTickInterval(1000)
        self.videoWidget.setScaleMode(0)

        QtCore.QObject.connect(self.mediaObject, QtCore.SIGNAL('tick(qint64)'),self.tick)
        QtCore.QObject.connect(self.mediaObject,QtCore.SIGNAL('stateChanged(Phonon::State, Phonon::State)'),self.stateChanged)
        QtCore.QObject.connect(self.metaInformationResolver,QtCore.SIGNAL('stateChanged(Phonon::State, Phonon::State)'),self.metaStateChanged)
        QtCore.QObject.connect(self.mediaObject,QtCore.SIGNAL('currentSourceChanged(Phonon::MediaSource)'),self.sourceChanged)
        
        self.setupActions()
       # self.setupMenus()
        self.setupUi2()
        self.timeLcd.display("00:00")

        self.video_id = self.videoWidget.winId()
        self.source = ''

    def muting(self):
        if self.audioOutput.isMuted():
            self.audioOutput.setMuted(0)
            self.muteAction.setIcon(QtGui.QIcon("mute_off.png"))
        else:
            self.audioOutput.setMuted(1)
            self.muteAction.setIcon(QtGui.QIcon("mute_on.png"))
		
    def sizeHint(self):
        return QtCore.QSize(600, 450)

    def addFiles(self,string):
        self.source = Phonon.MediaSource(string)
        if self.source: self.metaInformationResolver.setCurrentSource(self.source)

    def stateChanged(self, newState, oldState):
        if newState == Phonon.ErrorState:
            if self.mediaObject.errorType() == Phonon.FatalError:
                QtGui.QMessageBox.warning(self, self.tr("Fatal Error"),self.mediaObject.errorString())
            else:
                QtGui.QMessageBox.warning(self, self.tr("Error"),self.mediaObject.errorString())

        elif newState == Phonon.PlayingState:
            self.playAction.setEnabled(False)
            self.pauseAction.setEnabled(True)
            self.stopAction.setEnabled(True)

        elif newState == Phonon.StoppedState:
            self.stopAction.setEnabled(False)
            self.playAction.setEnabled(True)
            self.pauseAction.setEnabled(False)
            self.timeLcd.display("00:00")

        elif newState == Phonon.PausedState:
            self.pauseAction.setEnabled(False)
            self.stopAction.setEnabled(True)
            self.playAction.setEnabled(True)

    def tick(self, time):
        displayTime = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
        self.timeLcd.display(displayTime.toString('mm:ss'))

    def sourceChanged(self, source):
        self.timeLcd.display("00:00")

    def metaStateChanged(self, newState, oldState):
        if newState == Phonon.ErrorState:
            QtGui.QMessageBox.warning(self, self.tr("Error opening files"),
                    self.metaInformationResolver.errorString())

        self.mediaObject.setCurrentSource(self.metaInformationResolver.currentSource())

        source = self.metaInformationResolver.currentSource()

    # I know, it might be one func but... err, that was faster to ctrl+c/v
    def aspect_auto(self): self.videoWidget.setAspectRatio(0)
    def aspect_user(self): self.videoWidget.setAspectRatio(1)
    def aspect_43(self): self.videoWidget.setAspectRatio(2)
    def aspect_169(self): self.videoWidget.setAspectRatio(3)

    def scale_fit(self): self.videoWidget.setScaleMode(0)
    def scale_scale(self): self.videoWidget.setScaleMode(1)

    def change_stylecleanlooks(self): change_style(app,'cleanlooks')
    def change_styleplastique(self): change_style(app,'plastique')

    def setupActions(self):

        self.playAction = QtGui.QAction(QtGui.QIcon("play.png"), "Play", self.tab_2)
        self.playAction.setShortcut("Crl+P")
        self.playAction.setDisabled(True)

        self.pauseAction = QtGui.QAction(QtGui.QIcon("pause.png"), "Pause", self.tab_2)
        self.pauseAction.setShortcut("Ctrl+A")
        self.pauseAction.setDisabled(True)

        self.stopAction = QtGui.QAction(QtGui.QIcon("stop.png"), "Stop", self.tab_2)
        self.stopAction.setShortcut("Ctrl+S")
        self.stopAction.setDisabled(True)

        self.muteAction = QtGui.QAction(QtGui.QIcon("mute_off.png"), "Mute", self.tab_2)
        self.muteAction.setShortcut("Ctrl+M")

        self.addFilesAction = QtGui.QAction("Open...", self.tab_2)
        self.addFilesAction.setShortcut("Ctrl+F")

        # connections
        QtCore.QObject.connect(self.playAction, QtCore.SIGNAL('triggered()'),self.mediaObject, QtCore.SLOT('play()'))
        QtCore.QObject.connect(self.pauseAction, QtCore.SIGNAL('triggered()'),self.mediaObject, QtCore.SLOT('pause()'))
        QtCore.QObject.connect(self.stopAction, QtCore.SIGNAL('triggered()'),self.mediaObject, QtCore.SLOT('stop()'))
        QtCore.QObject.connect(self.muteAction, QtCore.SIGNAL('triggered()'),self.muting)
        QtCore.QObject.connect(self.addFilesAction, QtCore.SIGNAL('triggered()'),self.addFiles)

 
    def setupUi2(self):
        bar = QtGui.QToolBar(self.tab_2)
        bar.setGeometry(QtCore.QRect(700, 535, 140, 23))
        bar.addAction(self.playAction)
        bar.addAction(self.pauseAction)
        bar.addAction(self.stopAction)
        bar.addAction(self.muteAction)

        self.seekSlider = Phonon.SeekSlider(self.tab_2)
        self.seekSlider.setGeometry(QtCore.QRect(200, 470, 551, 19))
        self.seekSlider.setObjectName(_fromUtf8("seekSlider"))
        
        self.seekSlider.setMediaObject(self.mediaObject)

        self.volumeSlider = Phonon.VolumeSlider(self.tab_2)
        self.volumeSlider.setGeometry(QtCore.QRect(730, 510, 109, 22))
        self.volumeSlider.setObjectName(_fromUtf8("volumeSlider"))
        self.volumeSlider.setAudioOutput(self.audioOutput)
        self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Maximum)

        volumeLabel = QtGui.QLabel()
        volumeLabel.setPixmap(QtGui.QPixmap('volume.png'))

        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Light, QtCore.Qt.darkGray)

        self.timeLcd = QtGui.QLCDNumber(self.tab_2)
        self.timeLcd.setPalette(palette) 
        self.timeLcd.setGeometry(QtCore.QRect(760, 470, 81, 23))
        self.timeLcd.setObjectName(_fromUtf8("lcdNumber"))

        seekerLayout = QtGui.QHBoxLayout()
        seekerLayout.addWidget(self.seekSlider)
        seekerLayout.addWidget(self.timeLcd)

        playbackLayout = QtGui.QHBoxLayout()
        playbackLayout.addWidget(bar)
        playbackLayout.addStretch()
        playbackLayout.addWidget(volumeLabel)
        playbackLayout.addWidget(self.volumeSlider)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.videoWidget)
        
        mainLayout.addLayout(seekerLayout)
        mainLayout.addLayout(playbackLayout)
   
        
        
    def add_existing_files(self):
        config_file=0
        print("add existing files")
        config_file = open("config.txt", 'r')
        
        folder_path_list=[]
        folder_list=[]
        if not config_file:
            print("could not open config.txt")
        for line in config_file:   # czyta plik konfiguracyjny 
            #if line.split(" ")[0] == "photos" or line.split(" ")[0] == "videos": # gdy znajedzie linie mowiaca o foto  lub video to notuje
            if  line.split(" ")[0] == "videos": # gdy znajedzie linie mowiaca o foto  lub video to notuje
                folder_path = line.split(" ")[1].strip()                         #sciezke do folderu zawierajacego zdjecia
                #$$$$$$$$$$$
                folder= FolderWithItems(folder_path)
                folder_list.append(folder)
                #$$$$$$$$$$$
                folder_path_list.append(folder_path)
                #print os.listdir(folder_path)
                #print os.listdir('C:\\Users\\noname\\Pictures\\interferogram\\photos\\')
                
                list_of_files=[]
                folder_path = os.path.abspath('')+"\..\workspace\\"
                try:
                    list_of_files = os.listdir(folder_path)
                    print "wyluskalem sciezke ",folder_path, "sa w niej " ,list_of_files 
                except IOError as (errno, strerror):
                    print "I/O error({0}): {1}".format(errno, strerror)
                except ValueError:
                    print "Could not convert data to an integer."
                except:
                    print "Unexpected error:", sys.exc_info()[0]
            
                # dodanie zdjec i video do widgetow
                for file_object in list_of_files:	
                          #files_in_folder=         
                    try: 				
                        item_path=folder_path  + file_object
                        print(item_path)
                        self.add_item(item_path)
                    except:
                        print("could not add: " , item_path ," to list widget")
                        
        #thread.start_new_thread(self.update_listwidgets, (folder_list,))                        
   
    def update_listwidgets(self,folder_list):
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
       

