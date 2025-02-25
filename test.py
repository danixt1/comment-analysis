from src.output.graphics.lineGraphic import PercentageBehaviorLineGraphic
from src.output.graphics.intervalMaker import DateInterval
from src.datasets.makeDataset import makeData,commentData
from src.comment import Comment
from datetime import datetime

start = datetime(2018, 1, 1).timestamp()
end = datetime(2018, 6, 1).timestamp()

seed = 'seed of the test'
data = makeData(100,seed=seed,useDataStructure=commentData,maxPositives=0.7)

nextValue = (end - start) / len(data)
comments = [Comment(**x) for x in data]
    
timestamps = [start + nextValue * x for x in range(len(data))]
timestampsWithValues = list(zip(timestamps, comments))
interval = DateInterval(timestampsWithValues,timestampInSeconds=True)
graphic = PercentageBehaviorLineGraphic(interval)
graphic.save('test')

import os
os.system('test.png')