import numpy as np
from .graphic import BaseGraphic

POSITIVE_COLOR = '#67d658'
NEGATIVE_COLOR = '#f23838'
QUESTION_COLOR = '#f2ec38'
NEUTRAL_COLOR = '#bfbfbf'

class StackGraphic(BaseGraphic):
    gname = 'stack'
    def _makeData(self, intervals):
        keys = ['positive','negative','neutral','question']
        behaviors = {key:[] for key in keys}

        for comments in intervals.getIntervals():
            for key in keys:
                behaviors[key].append(0)

            for comment in comments:
                behavior = comment.getData()['behavior']
                behaviors[behavior][-1] += 1
        return behaviors
    
    def _plot(self, legends, data, ax):
        colors=[POSITIVE_COLOR,NEGATIVE_COLOR,NEUTRAL_COLOR,QUESTION_COLOR]
        values = data.values()
        max_value = max(np.sum([*values], axis=0)) + 2
        intervals = int(max_value / 10 ) or 1
        labels = data.keys()
        ax.stackplot(legends, values,colors=colors, labels=labels, alpha=1)
        ax.legend(loc='upper left', reverse=False)
        ax.set(yticks=np.arange(intervals,max_value,intervals))
