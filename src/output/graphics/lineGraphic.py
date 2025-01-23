import numpy as np

from .graphic import DateGraphic

class LineGraphic(DateGraphic):
    gname = "line"
    def _plot(self,legends, data, ax):
        ax.plot(legends, data, linewidth=2.0)
        ax.set_yticks(np.arange(0, 101, 10))
class PercentageBehaviorLineGraphic(LineGraphic):
    gname = "percentageBehaviorLine"
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
class ProblemsLineGraphic(LineGraphic):
    gname = "problemsLine"
    def _plot(self,legends, data, ax):
        for label,values in data.items():
            ax.plot(legends, values, linewidth=2.0, label=label)
        #ax.plot(legends, data, linewidth=2.0)
        #ax.set_yticks(np.arange(0, 101, 10))
    def _makeData(self, intervals):
        problems = {}
        count = 0
        for comments in intervals.getIntervals():
            for comment in comments:
                lastData = comment.getData()
                if lastData == None:
                    continue
                if "problems" not in lastData:
                    continue
                for problem in lastData['problems']:
                    if problem not in problems:
                        problems[problem] = [0]
                    if len(problems[problem]) <= count:
                        problems[problem].extend([0] * (count - len(problems[problem]) + 1))
                    problems[problem][count] +=1
            count += 1
        return problems