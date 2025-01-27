from src.cache import Cache
from src.comment import Comment,CommentScorer
from src.aiclient.pipeline import Pipe,Controller,PipeRunner
from src.aiclient.process import Process,RequestProcess
from src.aiclient.client import AiClient
from src.aiclient.promptInfo import PromptInfo
import logging
logger = logging.getLogger(__name__)


# Cache
def activateCache(main:AiClient,data):
    if not hasattr(main,"_cache"):
        return False
    data['cache'] = main._cache
    return True

def getFromCache(data,cache:Cache,process:Process,controller:Controller):
    comments = data['comments']
    cached = cache.get()
    if not cached:
        return
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
        controller.finish()
        process.finish()
        return process.toDict()
    data['comments'] = ret

def saveToCache(batch:list[Comment],cache:Cache):
    
    data = []
    for index in range(len(batch)):
        process = batch[index].getLastProcess()
        if process == None:
            continue
        data.append([batch[index].localId,process])
    cache.add(data)

# Batchs
def addBatchs(main:AiClient,comments:list[Comment], data):
    batchs = main._separateCommentsBatch(comments)
    batchs = [x for x in batchs if len(x)]
    data['batchs'] = batchs
def prepareBatchsToProcess(main:AiClient,process:Process, data,batchs:list[list[Comment]]):
    reqInfos = []
    for batch in batchs:
        prompt = main._generatePrompt(batch)
        index = process.addBatch(prompt,batch)
        reqInfos.append([batch,prompt,index])
    data['request_data'] = reqInfos

# Requests
def makeRequests(data,controller:Controller):
    reqInfos = data['request_data']
    for batch, prompt, index in reqInfos:
        controller.instancePipe('requestToAi',{'batch':batch,'prompt':prompt,'index':index})

def requestData(batch:list[Comment],prompt:PromptInfo,index:int,main:AiClient,process:Process,controller:Controller,data):
    logger.info(f"client {main.clientName}:requesting analyze for batch with {len(batch)} comments...")
    maxRetrys = 4
    while maxRetrys:
        maxRetrys-=1
        requestData = RequestProcess( prompt, batch)
        main._makeRequestToAi(str(prompt),requestData)
        if requestData.error:
            requestData.finish()
            process.getRequest(requestData, index)
            error,msg = requestData.error
            if error in ["timeout","connection"]:
                logger.warning(f"client {main.clientName}:Failed requesting api data, error:{error}, msg:{msg}, retrying...")
                continue
            logger.error(f"client {main.clientName}:Critical error process finished, error {error}, mgs:{msg}")
            controller.finish()
            return
        dataInRequest = requestData.data
        if len(dataInRequest) > len(batch):
            requestData.setHallucinationError("Returned more data than the expected").finish()
            process.getRequest(requestData, index)
            controller.finish()
            return
        data['requestData'] = requestData
        return

def attachDataFromRequest(main:AiClient,requestData:RequestProcess,batch:list[Comment], process:Process):
    data = requestData.data
    for i in range(len(data)):
        message,msgData = batch[i],data[i]
        message.attachInfo(msgData, main.clientName, process.id)
        
def endRequest(requestData:RequestProcess,process:Process,index:int):
    requestData.finish()
    process.getRequest(requestData,index)

# Scorer

activateScorer = lambda main: main.autoTestPercentage > 0.0

def onPipesCreatedScorer(pipe:Pipe,pipes,data,main:AiClient):
    if main.autoTestPercentage == 0.0:
        return
    data['autoTestPercentage'] = main.autoTestPercentage
    #FIX: its dont tell if cache is active or not.
    pipe.after('getFromCache',addTestComments)
    pipe.before('addBatchs',addTestComments)

def addTestComments(data,comments:list[Comment]):
    from src.datasets.makeDataset import makeData
    quantity = int(len(comments) * data['autoTestPercentage']) or 1
    distribuition = int(len(comments) / quantity)
    tests = makeData(quantity)
    tests = [CommentScorer(**x) for x in tests]
    data['comments'] = [x for x in comments]
    testIndex =0
    for i in range(len(comments) -1,0,-distribuition):
        data['comments'].insert(i, tests[testIndex])
        testIndex+=1 
def removeTestsComment(requestData:RequestProcess,main,index,data):
    batch = data['batch']
    scores = []
    for x in batch:
        if isinstance(x, CommentScorer):
            scores.append(x.getScore())
    if len(scores) > 0:
        requestData.setScore(scores)
        logger.info(f"client {main.clientName}:score for batch {index} is {requestData.score.totalScore}")
    data['batch'] = [x for x in batch if not isinstance(x, CommentScorer)]


def initPipeRunner(runner:PipeRunner):
    runner.createPipe('cache',activateCache).before('addBatchs', getFromCache).after('endRequest',saveToCache)
    runner.createPipe("batchs").add(addBatchs,prepareBatchsToProcess)
    runner.createPipe("requests").add(makeRequests)
    runner.createPipe('scorer',activateScorer).after('attachDataFromRequest', removeTestsComment).onPipesCreated(onPipesCreatedScorer)
    runner.createInstanciablePipe('requestToAi').add(requestData, attachDataFromRequest, endRequest)