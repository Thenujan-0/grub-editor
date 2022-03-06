#How it works?

There is a class defined in the name of TestProgress
which inherits from ProgressUi(the class to test)  and TestFunctions(which has useful functions that will be connected to some worker signals)

A window will be created from this class so that it will contain everything from the class to test as well as the functions that we need to run in mainloop in order to test




It uses unittest.main() as the start

the UnitTest_.test_() will be called by the above line
It will start the main function with UnitTest.TestCase obj and an executable string as arguments

the main function will  
&nbsp;&nbsp;&nbsp;initialize the QApplication,  
&nbsp;&nbsp;&nbsp;create A Window,  
&nbsp;&nbsp;&nbsp;show the window,  
&nbsp;&nbsp;&nbsp;start execution of QApplication

