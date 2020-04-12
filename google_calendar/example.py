'''
Created on Nov 16, 2018

@author: mbuerl
'''

import sys
import os
import time
import shutil
import json
import logging
import _thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



def getConfigurations():

    configfilepath = os.path.dirname(os.path.realpath(sys.argv[0]))

    #get configs
    configurationFile = configfilepath + '\\config.json'
    print(configurationFile)
    configurations = json.loads(open(configurationFile).read())
    
    return configurations


configurations = getConfigurations()

class FolderWatcher:

    DIRECTORY_TO_WATCH = configurations["startPath"]
    
    def __init__(self):
        self.observer = Observer()
           
    def run (self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print ("Error")   
        
        self.observer.join()


    def folderchecker(self):
    #checks if startDir is empty at the start
        listlength = len(os.listdir(self.DIRECTORY_TO_WATCH))

        if listlength == 0:
            print("Nothing")
        else:
            h = Handler()
            h.foldercleaner(self.DIRECTORY_TO_WATCH, listlength)
            
        
        
class Handler(FileSystemEventHandler):
        
    def on_any_event(self, event):
        if event.is_directory:
            return None
        
        elif event.event_type == 'created':
            eventpath = event.src_path
            filename = self.getfilename(eventpath)
            print ("File %s created:   %s" % (filename, event.src_path))
            self.furtherActions(eventpath,filename)
                
#        elif event.event_type == 'moved':
#           eventpath = event.src_path
#           filename = self.getfilename(eventpath) 
#           print ("File %s moved from: %s to %s" % (filename, event.src_path, event.dest_path))
#           self.furtherActions(eventpath,filename)
    #        
#       elif event.event_type == 'modified':
#          eventpath = event.src_path
#          filename = self.getfilename(eventpath) 
#          print ("File %s modified:  %s" % (filename, event.src_path))
#          self.furtherActions(eventpath,filename)
            
        elif event.event_type == 'deleted':
            eventpath = event.src_path
            filename = self.getfilename(eventpath) 
            print ("File %s deleted:   %s" % (filename, event.src_path))
          
                
    def getfilename(self, usedpath):
        filename = os.path.basename(usedpath)
        return filename    
    
    def getnamesplit(self,eventpath):
        if configurations["splitSign"] in eventpath:
            splitname = os.path.basename(eventpath).split(configurations["splitSign"])[0]
            actionstate = True
        else:
            splitname = "No proper to split sign"
            actionstate = False
        return splitname, actionstate
    
    def furtherActions(self,eventpath,filename):
        fexist = os.path.exists(eventpath)
        if fexist == True:
            nogrowth = False
            fread = False
            fwrite = False
            while fexist == True:
                if nogrowth == True and fread == True and fwrite == True:
                    splittedname, actionstate = self.getnamesplit(eventpath)
                    if actionstate == True:
                        m = Mover()
                        m.pathchecker(splittedname,eventpath,filename)
                        break
                    else:
                        #some feedback to user that he needs to insert proper splitting sign
                        print ("nofurtheractions")
                    break
                else:
                    try:
                        nogrowth = self.filegrowth(eventpath)
                        #print (nogrowth)
                        fread, fwrite = self.faccess(eventpath)
                        #print (fread, fwrite)
                    except:
                        print("error while trying to get infos about file: %s" % eventpath)
                    time.sleep( 10 )
                    fexist = os.path.exists(eventpath)
        else:
            print ("file % got deleted in the meantime" % filename)


    def foldercleaner(self, path, length):
        #cleans startDir at the start
        filelist = os.listdir(path)
        print ("Folder was not empty. Files %s will get moved" % filelist)
        i = 0
        while i < length:
            eventpath = path + filelist[i]
            filename = filelist[i]
            self.furtherActions(eventpath,filename)
            #print(eventpath,filename, length)
            time.sleep( 2 )
            if len(filelist) == 0:
                break
            i = i + 1
                        
            
    def filegrowth(self, eventpath):
        try:
            oldsize = os.path.getsize(eventpath)
            #keep in mind: os.stat(eventpath).st_size! other endings with more values possible
            time.sleep ( 10 )
            newsize = os.path.getsize(eventpath)
            if oldsize == newsize:
                nogrowth = True
            else:
                nogrowth = False
        except:
            print ("checking of file size failed!")
            
        return nogrowth


    def faccess(self, eventpath):
        try:
            fread = os.access(eventpath, os.R_OK)
            time.sleep ( 2 )
            fwrite = os.access(eventpath, os.W_OK)
        except:
            print ("check for accessability failed: %s" % eventpath)
            
        return fread , fwrite
              
            
class Mover:
    h = Handler()
    def pathchecker(self,splittedname,eventpath,filename):
        startfile = eventpath
        destfolder = configurations["endPath"] + splittedname + "/"
        destfile = destfolder + filename
        #print ("startfile %s, destfolder %s, destfile %s" %(startfile,destfolder,destfile))
        try:
            pathstate = os.path.exists(destfolder)
        except:
            print("path finding error")
        if pathstate == True:
            self.filemover(startfile,destfile,filename)
        else:
            _thread.start_new_thread(self.pathwatcher, (pathstate,destfolder,startfile,destfile))

    def pathwatcher(self,pathstate,destfolder,startfile,destfile):
        print ("watcherstart")
        while pathstate == False:
            print ("checking")
            pathstate = os.path.exists(destfolder)
            if pathstate == True:
                try:
                    _thread.start_new_thread(self.filemover, (startfile,destfile))
                    time.sleep ( 0 )
                    _thread.exit()
                    break
                except:
                    time.sleep( 0 )
            else:
                fileexist = os.path.exists(startfile)
            if fileexist == False: #checks if file is still there. important if removed by user
                print("im gone")
                _thread.exit()
                break
            else:
                time.sleep( 5 )
            
            
    def filemover(self,startfile, destfile, filename):
        fmovability = False
        while fmovability == False:
            try:
                shutil.move(startfile , destfile)
                print ("the file %s got moved: from \" %s \" to \" %s \"" % (filename,startfile,destfile))
                fmovability = True
            except:
                print("file is not movable")
                try:
                    fexist = os.path.exists(startfile)
                    if fexist == False:
                        print ("File %s got removed before proper moving was passible." % filename)
                        _thread.exit()
                        break
                    else:
                        time.sleep( 10 )
                except:
                    time.sleep ( 0 )
            if fmovability == True:
                try:
                    _thread.exit()
                except:
                    break
            else:
                time.sleep ( 0 )




if __name__ == "__main__":
    watcher = FolderWatcher()
    watcher.folderchecker()
    watcher.run()

