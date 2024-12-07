import matplotlib.pyplot as plt
import numpy as np

from .intervalMaker import DateInterval

class PercentageGraphic:
    def __init__(self,dateInterval:DateInterval,title = None,max_data=6,size = (10,3)):
        x,y = self._generate_data(dateInterval)
        fig = plt.figure(figsize=size)
        ax = fig.add_subplot()
        ax.set( yticks=np.arange(0, 101,10),ylim=(0,101))
        def plot():
            if title:
                ax.set_title(title)
            ax.plot(x, y, linewidth=2.0)
        self.plot = plot
    def save(self,path):
        self.plot()
        plt.savefig(path)

    def _generate_data(self,dateInterval:DateInterval):
        partValues = []

        for comments in dateInterval.getIntervals():
            accNegatives = 0
            accPositives = 0
            for comment in comments:
                lastData = comment.getData()
                if lastData == None:
                    continue
                if lastData['behavior'] == 'positive':
                    accPositives+= 1
                elif lastData['behavior'] == 'negative':
                    accNegatives+= 1
            total = accPositives + accNegatives
            if total == 0:
                partValues.append(0)
                continue
            partValues.append((1 - (accNegatives / total)) * 100)
        
        return dateInterval.getLegends(),partValues
