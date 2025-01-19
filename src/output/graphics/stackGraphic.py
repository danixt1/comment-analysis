import numpy as np
from .graphic import DateGraphic

POSITIVE_COLOR = '#67d658'
NEGATIVE_COLOR = '#f23838'
QUESTION_COLOR = '#f2ec38'
NEUTRAL_COLOR = '#bfbfbf'

class StackGraphic(DateGraphic):
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
        intervals = int(max_value / 7 ) or 1
        labels = list(data.keys())
        bottom = np.zeros(len(legends))
        for label,d in data.items():
            arr = np.array(d)
            ax.bar(legends,arr,3,label=label,bottom=bottom,color = colors[labels.index(label)])
            bottom += arr
        #ax.stackplot(legends, values,colors=colors, labels=labels, alpha=1)
        ax.legend(loc='upper left', reverse=False)
        ax.set_yticks(np.arange(intervals,max_value,intervals))
