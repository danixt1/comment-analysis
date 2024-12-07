import numpy as np

from .graphic import BaseGraphic

class PercentageGraphic(BaseGraphic):
    def _plot(self,legends, data, ax):
        ax.set_yticks(np.arange(0, 101,10))
        ax.plot(legends, data, linewidth=2.0)
        
    def _makeData(self, intervals):
        partValues = []
        for comments in intervals.getIntervals():
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
        
        return partValues