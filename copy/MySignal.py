from PySide6.QtCore import Signal, QObject


class MySignal(QObject):
    setResult = Signal(str,int,int,int)
    setProgressBar = Signal()
    setResult2 = Signal(str,int,int,int)

my_signal = MySignal()