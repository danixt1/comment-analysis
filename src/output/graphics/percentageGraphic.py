from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from src.comment import Comment

class PercentageGraphic:
    def __init__(self,comments:list[Comment],title = None,max_data=6,size = (10,3)):
        x,y = self._generate_data(comments,max_data)
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

    def _generate_data(self,comments:list[Comment],limit):
        timestamps = [[x.timestamp,x.getData()['behavior']] for x in comments]
        timestamps = list(filter(lambda x:x[1] != 'question',timestamps))
        timestamps.sort()

        initTime = timestamps[0][0]
        endTime = timestamps[-1][0]
        intervals = (endTime - initTime) / limit
        limitInInterval = initTime + intervals

        partTimestamp = []
        partValues = []


        accNegatives = 0
        accPositives = 0
        for timestamp,behavior in timestamps:
            if timestamp >= limitInInterval:
                partValues.append((1 - (accNegatives / (accPositives + accNegatives))) * 100)#(1 - (1 / 4)) * 100
                accPositives = 0
                accNegatives = 0
                limitInInterval += intervals
                partTimestamp.append(limitInInterval)
            if behavior == 'positive':
                accPositives+= 1
            elif behavior == 'negative':
                accNegatives+= 1
        dates = [datetime.fromtimestamp(x / 1000) for x in partTimestamp]
        dates = [str(x.year) + '/'+str(x.month) for x in dates]
        return dates,partValues
