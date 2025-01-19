from abc import ABC,abstractmethod

from matplotlib.axes import Axes
from .intervalMaker import DateInterval
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.dates as mdates

class BaseGraphic(ABC):
    gname = 'not-set'
    def __init__(self,data,title:str = None, xlabel:str = None, ylabel:str = None,fig:Figure = None, axes:Axes = None):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.data = self._makeData(data)
        self.fig:Figure = fig
        self.axes:Axes = axes

    def subplot(self, **kwargs):
        self.fig, self.axes = plt.subplots(**kwargs)
        return self.fig,self.axes

    def makeGraphic(self):
        if self.fig and self.axes:
            fig = self.fig
            ax = self.axes

        if self.fig and not self.axes:
            fig = self.fig
            ax = fig.add_subplot()
            self.axes = ax

        if not self.fig and not self.axes:
            fig, ax = plt.subplots()
            self.fig = fig
            self.axes = ax
        self.plotInAxes(ax)
        return fig

    def plotInAxes(self, ax:Axes):
        self._plot(self.data, ax)
        self.setTexts(ax)

    def setTexts(self,ax:Axes):
        if self.title:
            self._setTitle(ax, self.title)
        if self.xlabel:
            self._setXLabel(ax, self.xlabel)
        if self.ylabel:
            self._setYLabel(ax, self.ylabel)

    def save(self, path:str):
        fig  = self.makeGraphic()
        fig.savefig(path)

    @abstractmethod
    def _makeData(self, data):
        pass

    @abstractmethod
    def _plot(self, data, ax:Axes):
        pass

    def _setTitle(self, ax:Axes, title:str):
        ax.set_title(title)

    def _setXLabel(self, ax:Axes, xlabel:str):
        ax.set_xlabel(xlabel)

    def _setYLabel(self, ax:Axes, ylabel:str):
        ax.set_ylabel(ylabel)

class DateGraphic(BaseGraphic):
    gname = 'not-set'
    def __init__(self, 
                 intervals:DateInterval, 
                 title:str = None, xlabel:str = None, ylabel:str = None,fig:Figure = None, axes:Axes = None):
        super().__init__(intervals, title, xlabel, ylabel, fig, axes)
        self.intervals = intervals
        self.legends = intervals.getLegends()
    
    def makeGraphic(self):
        super().makeGraphic()
        ax = self.axes

        granularity = self.intervals.granularity
        if granularity == 'year':
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        elif granularity == 'month':
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m'))
        
        return self.fig
    
    def plotInAxes(self, ax:Axes):
        self._plot(self.legends,self.data, ax)
        self.setTexts(ax)

    @abstractmethod
    def _makeData(self,intervals:DateInterval):
        pass

    @abstractmethod
    def _plot(self, legends, data, ax:Axes):
        pass