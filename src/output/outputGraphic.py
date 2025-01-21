from src.output.outputBase import OutputBase
from src.comment import Comment
from src.output.graphics.intervalMaker import DateInterval
import json
labelsData = None

class OutputGraphic(OutputBase):
    
    def __init__(self,filename:str = 'output',lang = 'en',granularity = None):
        if not filename.endswith('.png'):
            filename += '.png'
        self.path = filename
        self.lang = lang
        self.granularity = granularity
        global labelsData
        if not labelsData:
            with open('src/output/graphics/labels.json','r') as labels:
                labelsData = json.load(labels)

    def _makeGraphics(self,comments:list[Comment],lang = "en"):
        import matplotlib.pyplot as plt
        from src.output.graphics.percentageGraphic import PercentageGraphic
        from src.output.graphics.stackGraphic import StackGraphic
        from src.output.graphics.pieGraphic import PieGraphic
        timestampsAndComments = [(x.timestamp,x) for x in comments if x.timestamp is not None and x.getData() is not None]
        dateInterval = DateInterval(timestampsAndComments,granularity=self.granularity)
        langData = labelsData[lang]
        if dateInterval.endDate.timestamp() - dateInterval.startDate.timestamp() < 60 * 60 * 24 * 2:
            return
        fig,axes = plt.subplots(2,2,figsize=(15,7))
        plt.subplots_adjust(hspace= 0.45)
        percentage =PercentageGraphic(dateInterval,langData['median']['title'],fig=fig,axes=axes[0,0])
        stack = StackGraphic(dateInterval,langData['stack']['title'],fig=fig,axes=axes[1,0])
        pie = PieGraphic(comments, langData['pie']['title'], fig=fig, axes=axes[0,1])
        axes[1,1].axis('off')
        percentage.makeGraphic()
        pie.makeGraphic()
        stack.save(self.path)
    def sendData(self, comments, processResults):
        self._makeGraphics(comments,self.lang)