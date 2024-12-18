from src.cache import Cache
from src.comment import Comment,CommentScorer
from src.iaclient.pipeline import Pipe,Controller
from src.iaclient.process import Process,RequestProcess
from src.iaclient.client import IAClient
from src.iaclient.promptInfo import PromptInfo
import logging
logger = logging.getLogger(__name__)

def CreatePipeCache():
    def activateCache(main:IAClient,data):
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

    def saveToCache(comments:list[Comment],cache:Cache):
        data = []
        for index in range(len(comments)):
            process = comments[index].getLastProcess()
            if process == None:
                continue
            data.append([comments[index].localId,process])
        cache.add(data)

    onPipesCreatedCache = lambda pipe,pipes: pipe.after('clearCommentScore' if 'scorer' in pipes else 'dataRequested',saveToCache)
    return Pipe("cache",activator=activateCache).before('addBatchs',getFromCache).onPipesCreated(onPipesCreatedCache)

def createBatchPipe():
    def addBatchs(main:IAClient,comments:list[Comment], data):
        batchs = main._separateCommentsBatch(comments)
        batchs = [x for x in batchs if len(x)]
        data['batchs'] = batchs
    def prepareBatchsToProcess(main:IAClient,process:Process, data,batchs:list[list[Comment]]):
        reqInfos = []
        for batch in batchs:
            prompt = main._generatePrompt(batch)
            index = process.addBatch(prompt,batch)
            reqInfos.append([batch,prompt,index])
        data['request_data'] = reqInfos
    return Pipe("batchs").add(addBatchs,prepareBatchsToProcess)
def createRequestPipe():
    def makeRequests(main:IAClient, data,process:Process,controller:Controller):
        reqInfos = data['request_data']
        resultInfo = []
        for batch, prompt, index in reqInfos:
            subPipe = Pipe('request').add(requestData,attachDataFromRequest,endRequest)
            controller.addSubPipe(subPipe)

    
    def requestData(batch:list[Comment],prompt:PromptInfo,index:int,main:IAClient,process:Process):
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
                break
            data = requestData.data
            if len(data) > len(batch):
                requestData.setHallucinationError("Returned more data than the expected")
                requestData.finish()
            data['requestData'] = requestData
            break

    def attachDataFromRequest(main:IAClient,requestData:RequestProcess,batch:list[Comment], process:Process):
        data = requestData.data
        for i in range(len(data)):
            message,msgData = batch[i],data[i]
            message.attachInfo(msgData, main.clientName, process.id)
    def endRequest(requestData:RequestProcess,proccess:Process,index:int):
        requestData.finish()
        proccess.getRequest(requestData,index)

    
    #return Pipe("request").add(makeRequests)

def createScoreComment():
    def addTestComments(data,comments:list[Comment]):
        from src.datasets.makeDataset import makeData
        quantity = int(len(comments) * data['autoTestPercentage']) or 1
        distribuition = int(len(comments) / quantity)
        tests = makeData(quantity)
        tests = [CommentScorer(**x) for x in tests]
        comments = [x for x in comments]
        testIndex =0
        for i in range(len(comments) -1,0,-distribuition):
            comments.insert(i, tests[testIndex])
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