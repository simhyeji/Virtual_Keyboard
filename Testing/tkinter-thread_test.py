import threading

class BackgroundTask():

    def __init__( self, taskFuncPointer ):
        self.__taskFuncPointer_ = taskFuncPointer
        self.__workerThread_ = None
        self.__isRunning_ = False

    def taskFuncPointer( self ) : return self.__taskFuncPointer_

    def isRunning( self ) : 
        return self.__isRunning_ and self.__workerThread_.isAlive()

    def start( self ): 
        if not self.__isRunning_ :
            self.__isRunning_ = True
            self.__workerThread_ = self.WorkerThread( self )
            self.__workerThread_.start()

    def stop( self ) : self.__isRunning_ = False

    class WorkerThread( threading.Thread ):
        def __init__( self, bgTask ):      
            threading.Thread.__init__( self )
            self.__bgTask_ = bgTask

        def run( self ):
            try :
                self.__bgTask_.taskFuncPointer()( self.__bgTask_.isRunning )
            except Exception as e: print (repr(e))
            self.__bgTask_.stop()

def tkThreadingTest():

    from tkinter import Tk, Label, Button, StringVar
    from time import sleep

    class UnitTestGUI:

        def __init__( self, master ):
            self.master = master
            master.title( "Threading Test" )

            self.threadedButton = Button( 
                self.master, text="Threaded", command=self.onThreadedClicked )
            self.threadedButton.pack()

            self.cancelButton = Button( 
                self.master, text="Stop", command=self.onStopClicked )
            self.cancelButton.pack()

            self.statusLabelVar = StringVar()
            self.statusLabel = Label( master, textvariable=self.statusLabelVar )
            self.statusLabel.pack()

            self.bgTask = BackgroundTask( self.myLongProcess )

        def close( self ) :
            print ("close")
            try: self.bgTask.stop()
            except: pass
            self.master.quit()

        def onThreadedClicked( self ):
            print ("onThreadedClicked")
            try: self.bgTask.start()
            except: pass

        def onStopClicked( self ) :
            print ("onStopClicked")
            try: self.bgTask.stop()
            except: pass

        def myLongProcess( self, isRunningFunc=None ) :
            print ("starting myLongProcess")
            # WORKING THREAD
            for i in range( 1, 10 ):
                try:
                    if not isRunningFunc() :
                        self.onMyLongProcessUpdate( "Stopped!" )
                        return
                except : pass   
                self.onMyLongProcessUpdate( i )
                # HERE
                # HERE
                # HERE
                sleep( 1.5 ) # simulate doing work
                # HERE
                # HERE
                # HERE
            self.onMyLongProcessUpdate( "Done!" )                

        def onMyLongProcessUpdate( self, status ) :
            print ("Process Update: %s" % (status,))
            self.statusLabelVar.set( str(status) )

    root = Tk()    
    gui = UnitTestGUI( root )
    root.protocol( "WM_DELETE_WINDOW", gui.close )
    root.mainloop()

if __name__ == "__main__": 
    tkThreadingTest()