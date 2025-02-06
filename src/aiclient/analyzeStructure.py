from src.cache import Cache
from src.comment import Comment,CommentScorer
from .process import Process
from .client import AiClient
from .requestProcess import RequestProcess
from .promptInfo import PromptInfo

import logging
from enum import Enum

logger = logging.getLogger(__name__)

class ResultEnum(Enum):
    STOP = 1
    CONTINUE = 2
    ERROR = 3
    SKIP = 4

def cacheActive(data,resultFn):
    if not hasattr(data['main'],"_cache"):
        return resultFn(ResultEnum.SKIP)
    data['cache'] = data['main']._cache
    return resultFn(ResultEnum.CONTINUE)

def cacheGetCachedComments(data,resultFn):
    if not 'cache' in data:
        return resultFn(ResultEnum.SKIP)
    comments = data['comments']
    cache = data['cache']
    process:Process = data['process']
    cached = cache.get()
    if not cached:
        return resultFn(ResultEnum.CONTINUE)
    cached = {id:data for id,data in cached}
    ret = []
    for comment in comments:
        localId = comment.localId
        if localId in cached:
            comment.process.append(cached[localId])
            continue
        ret.append(comment)
    if len(ret) == 0:
        logger.info(f"client {data['clientName']}:all comments already processed")
        process.finish()
        return resultFn(ResultEnum.STOP)
    data['comments'] = ret
    resultFn(ResultEnum.CONTINUE)

def cacheSaveRequestComments(data,resultFn):
    if not 'cache' in data:
        return resultFn(ResultEnum.SKIP)
    batch:list[Comment] = data['batch']
    cache:Cache = data['cache']
    cacheData = []
    for index in range(len(batch)):
        process = batch[index].getLastProcess()
        if process == None:
            continue
        cacheData.append([batch[index].localId,process])
    cache.add(cacheData)
    return resultFn(ResultEnum.CONTINUE)

# Batchs

def batchGenerateBatch(data,resultFn):
    main:AiClient = data['main']
    comments:list[Comment] = data['comments']
    batchs = main._separateCommentsBatch(comments)
    batchs = [x for x in batchs if len(x)]
    data['batchs'] = batchs
    return resultFn(ResultEnum.CONTINUE)

def _batchGeneratePrompt(data,batch:list[Comment]):
    main:AiClient = data['main']
    process:Process = data['process']
    prompt = main._generatePrompt(batch)
    index = process.addBatch(prompt,batch)
    return [batch,prompt,index]

def batchPrepareBatchsToProcess(data,resultFn):
    """Generate the final string prompt"""
    batchs:list[list[Comment]] = data['batchs']
    reqInfos = []
    for batch in batchs:
        reqInfos.append(_batchGeneratePrompt(data,batch))
    data['request_data'] = reqInfos
    resultFn(ResultEnum.CONTINUE)

# Requests
def requestTryFixError(data, resultFn):
    requestData:RequestProcess = data['requestData']
    error = requestData.error
    if not error:
        return resultFn(ResultEnum.SKIP)
    errorName = error[0]
    if errorName is not "hallucination" or errorName is not "partial-data":
        return resultFn(ResultEnum.ERROR)
    batch = data['batch']
    reqInfos = data['request_data']
    lenBatch = len(batch)
    if errorName is "hallucination":
        logger.warning(f"client {data['main'].clientName}:hallucination error, retrying processing {lenBatch} comments in this batch")
        for a in [batch[:lenBatch//2],batch[lenBatch//2:]]:
            reqInfos.append(_batchGeneratePrompt(data, a))
    else:
        newBatch = []
        totalNotProcessedComments = len(batch) - len(data['requestData'].data)
        if totalNotProcessedComments == 0:
            return resultFn(ResultEnum.SKIP)
        logger.warning(f"client {data['main'].clientName}:partial data error, retrying processing {totalNotProcessedComments} comments in this batch")
        startIndex = len(batch) - totalNotProcessedComments
        for i in range(startIndex, len(batch)):
            newBatch.append([batch[i]])
        reqInfos.append(_batchGeneratePrompt(data, newBatch))
    return resultFn(ResultEnum.CONTINUE)

def requestGenerateData(data,resultFn):
    batch:list[Comment] = data['batch']
    prompt:PromptInfo = data['prompt']
    index:int = data['index']
    main:AiClient = data['main']
    process:Process = data['process']

    logger.info(f"client {main.clientName}:requesting analyze for batch with {len(batch)} comments...")
    maxRetrys = 4
    while maxRetrys:
        maxRetrys-=1
        requestData = RequestProcess( prompt, batch)
        data['requestData'] = requestData
        main._makeRequestToAi(str(prompt),requestData)
        if requestData.error:
            requestData.finish()
            process.getRequest(requestData, index)
            error,msg = requestData.error
            if error in ["timeout","connection"]:
                logger.warning(f"client {main.clientName}:Failed requesting api data, error:{error}, msg:{msg}, retrying...")
                continue
            logger.error(f"client {main.clientName}:Critical error process finished, error {error}, mgs:{msg}")
            return resultFn(ResultEnum.ERROR)
        dataInRequest = requestData.data
        if len(dataInRequest) > len(batch):
            requestData.setHallucinationError("Returned {} more results than expected.".format(len(dataInRequest) - len(batch))).finish()
            process.getRequest(requestData, index)
            return resultFn(ResultEnum.ERROR)
        elif len(dataInRequest) < len(batch):
            requestData.setPartialDataError("Returned less data than the expected").finish()
            process.getRequest(requestData, index)
            return resultFn(ResultEnum.ERROR)
        return resultFn(ResultEnum.CONTINUE)

def requestAttachData(data,resultFn):
    main:AiClient = data['main']
    requestData:RequestProcess = data['requestData']

    batch:list[Comment] = data['batch']
    process:Process = data['process']
    reqData = requestData.data
    for i in range(len(reqData)):
        message,msgData = batch[i],reqData[i]
        message.attachInfo(msgData, main.clientName, process.id)
    return resultFn(ResultEnum.CONTINUE)

def requestEnd(data,resultFn):
    requestData:RequestProcess = data['requestData']
    index:int = data['index']
    process:Process = data['process']

    requestData.finish()
    process.getRequest(requestData,index)
    return resultFn(ResultEnum.CONTINUE)

# Scorer
def scorerAdd(data,resultFn):
    main:AiClient = data['main']
    if main.autoTestPercentage == 0.0:
        return resultFn(ResultEnum.SKIP)
    
    from src.datasets.makeDataset import makeData

    comments:list[Comment] = data['comments']
    quantity = int(len(comments) * main.autoTestPercentage) or 1
    distribuition = int(len(comments) / quantity)
    tests = makeData(quantity)
    tests = [CommentScorer(**x) for x in tests]
    data['comments'] = [x for x in comments]
    testIndex =0
    for i in range(len(comments) -1,0,-distribuition):
        data['comments'].insert(i, tests[testIndex])
        testIndex+=1 
    return resultFn(ResultEnum.CONTINUE)
#request
def scorerRemoveScorerFromRequest(data,resultFn):
    main:AiClient = data['main']
    requestData:RequestProcess = data['requestData']
    index:int = data['index']
    batch = data['batch']
    scores = []
    for x in batch:
        if isinstance(x, CommentScorer):
            scores.append(x.getScore())
    if len(scores) > 0:
        requestData.setScore(scores)
        logger.info(f"client {main.clientName}:score for batch {index} is {requestData.score.totalScore}")
    data['batch'] = [x for x in batch if not isinstance(x, CommentScorer)]
    return resultFn(ResultEnum.CONTINUE)
