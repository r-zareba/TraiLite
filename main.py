# This Python file uses the following encoding: utf-8


from PySide2.QtWidgets import QApplication
from PySide2 import QtQuick
from PySide2 import QtCore
from PySide2 import QtQml

from databases import databases
from backtesting import technicalsQT
from backtesting import backtest_visualizersQT
from backtesting import optimizersQT


class ThreadedTradingView(QtCore.QThread):

    def __init__(self, asset):
        super().__init__()
        # self.quotations = TradingView(asset)

        self.timer = QtCore.QTimer()
        self.timer.moveToThread(self)
        self.timer.timeout.connect(lambda: print('Hello'))

    def run(self):
        # print(self.quotations.get_price())
        self.timer.start(1000)
        loop = QtCore.QEventLoop()
        loop.exec_()


if __name__ == '__main__':
#
#    thread = ThreadedTradingView('EURUSD')
#    thread.start()

    """
    Register Python objects to QML stage
    """
    QtQml.qmlRegisterType(databases.PostgresManager,
                          'PostgresManager', 1, 0, 'PostgresManager')
    QtQml.qmlRegisterType(technicalsQT.StochasticBacktester,
                          'StochasticBacktester', 1, 0, 'StochasticBacktester')
    QtQml.qmlRegisterType(backtest_visualizersQT.BacktestChart,
                          'BacktestChart', 1, 0, 'BacktestChart')
    QtQml.qmlRegisterType(optimizersQT.StochasticOptimizer,
                          'StochasticOptimizer', 1, 0, 'StochasticOptimizer')

    app = QApplication(['TRAIS'])
    view = QtQuick.QQuickView()
    view.setResizeMode(QtQuick.QQuickView.SizeRootObjectToView)

    url = QtCore.QUrl('QML/main.qml')
    view.setSource(url)
    view.show()
    app.exec_()

