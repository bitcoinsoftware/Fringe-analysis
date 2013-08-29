import os
import sys
class FolderWithItems():
    number_of_files=0
    path=""
    
    def __init__(self, path):
        self.path=path.strip()
        try:
            self.number_of_files= len(os.listdir(path))
        except IOError as (errno, strerror):
            print "I/O error({0}): {1}".format(errno, strerror)
        except ValueError:
            print "Could not convert data to an integer."
        except:
            print "Unexpected error:", sys.exc_info()[0]
            #raise
        
    def get_number_of_files(self):
		self.number_of_files=len(os.listdir(self.path))
		return self.number_of_files
		
    def conntent_changed(self):
        number_of_files = self.number_of_files
        try:
            number_of_files= len(os.listdir(self.path))
        except IOError as (errno, strerror):
            print "I/O error({0}): {1}".format(errno, strerror)
        except ValueError:
            print "Could not convert data to an integer."
        except:
            print "Unexpected error:", sys.exc_info()[0]
        if number_of_files!=self.number_of_files:
            self.number_of_files = len(number_of_files)
            return 1
        else:
            return 0
