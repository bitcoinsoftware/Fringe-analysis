from distutils.core import setup
import py2exe

setup(windows=[{"script" : "koleszko26.py"}], data_files = [('phonon_backend', ['C:\Python27\Lib\site-packages\PyQt4\plugins\phonon_backend\phonon_ds94.dll'])], options={"py2exe" : {"includes" : ["sip", "PyQt4" ,"cv","scipy","PIL","PyQt4.QtSvg" ]}})

