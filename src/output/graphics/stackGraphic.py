import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from src.comment import Comment

POSITIVE_COLOR = '#67d658'
NEGATIVE_COLOR = '#f23838'
QUESTION_COLOR = '#f2ec38'
NEUTRAL_COLOR = '#bfbfbf'

class StackGraphic:
    def __init__(self,comments:list[Comment],title = None,ylabel = None,size = (10,3),max_data = 5):
        behaviors,dates = self._generate_data(comments, max_data)

        fig = plt.figure(figsize=size)
        ax = fig.add_subplot()

        max_value = max(np.sum([*behaviors.values()],axis=0)) + 2
        intervals =int( max_value / 10) or 1
        colors=[POSITIVE_COLOR,NEGATIVE_COLOR,NEUTRAL_COLOR,QUESTION_COLOR]
        
        ax.stackplot(dates, behaviors.values(),colors=colors, labels=behaviors.keys(), alpha=1)
        ax.legend(loc='upper left', reverse=False)

        if title:
            ax.set_title(title)
        if ylabel:
            ax.set_ylabel(ylabel)

        ax.set(yticks=np.arange(intervals,max_value,intervals),xlim=(0,max_data - 1),xticks=np.arange(0,max_data))
        plt.grid()

    def save(self, path):
        plt.savefig(path)

    def _generate_data(self,comments:list[Comment],limit:int):
        filtredComments = [comment for comment in comments if not comment.timestamp == None and comment.haveAdditionalData]
        limit = limit if len(filtredComments) > limit else len(filtredComments)
        behaviors = {'positive':[0],'negative':[0],'neutral':[0],'question':[0]}

        byTime = [[actTime.timestamp,actTime] for actTime in filtredComments]
        byTime.sort()
        initTime = byTime[0][0]
        endTime = byTime[-1][0]
        intervals = (endTime - initTime) / limit
        limitInInterval = initTime + intervals
        dates = [limitInInterval]

        for timestamp,data in byTime:
            if timestamp > limitInInterval:
                limitInInterval+=intervals
                dates.append(limitInInterval)
                for beKey in behaviors.keys():
                    behaviors[beKey].append(0)
            behavior = data.getData()['behavior']
            behaviors[behavior][-1] += 1

        dates = [datetime.fromtimestamp(x / 1000) for x in dates]
        dates = [str(x.year) + '/'+str(x.month) for x in dates]

        return behaviors,dates