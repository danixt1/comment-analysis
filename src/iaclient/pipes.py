from src.cache import Cache
from src.comment import Comment
from src.iaclient.pipeline import Pipe,Controller
from src.iaclient.process import Process,RequestProcess
from src.iaclient.client import IAClient
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
    return Pipe("cache",activator=activateCache).add(getFromCache).onPipesCreated(onPipesCreatedCache)

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
    def makeRequests(main:IAClient, data,process:Process):
        reqInfos = data['request_data']
        for batch, prompt, index in reqInfos:
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
    return Pipe("request").add()