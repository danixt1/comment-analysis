from pathlib import Path
import json
import re
import itertools
import random

commentsData = json.loads((Path(__file__).parent / 'comments_data.json').read_text(encoding='utf-8'))

MATCH_POSITIONS = r"\[([^\]]+)\]"
MATCH_FULL_POSITIONS = r"\[[^\]]+\]"
MATCH_VARIATIONS = r"[^|]+"


def normalizeData(data,msg):
    return {
        'message':msg,
        'type':data['type'] if 'type' in data else 'comment',
        'origin':'test',
        'spam':data['spam'] if 'spam' in data else False,
        'behavior':data['behavior'] if 'behavior' in data else '-',
        'min_problems':data['min_problems'] if 'min_problems' in data else 0,
        'problems':data['problems'] if "problems" in data else []
    }
def testerData(data):
    return {
        'message':data['message'],
        'type':data['type'],
        'origin':'test',
        "expected":{
            'spam':data['spam'],
            'behavior':data['behavior'],
            'min_problems':data['min_problems']
        }
    }
def commentData(data):
    return {
        'message':data['message'],
        'type':data['type'],
        'origin':'test',
        'process':[
            {
                "name":"test",
                "data":{
                    'spam':data['spam'],
                    'behavior':data['behavior'] if not data['behavior'] == '-' else 'neutral',
                    'problems':data['problems']
                },
                "process_id":random.randint(200,510000000)
            }
        ]
    }
def makeData(limit:int,exclude_tags = None,searchIn = commentsData,timestamps = None,maxPositives = 0.70,seed = None, useDataStructure = testerData):
    counts ={'positive':0, 'negative':0,'-':0}
    totalCount = 0
    stopProcess = False
    maxPositives = int(limit * maxPositives)
    comments = []
    addComment = lambda data,msg = None: comments.append(useDataStructure(normalizeData(data,msg)))
    def addToCount(behavior):
        nonlocal totalCount, stopProcess
        if behavior == 'positive' and counts['positive'] >= maxPositives:
            return False
        if totalCount >= limit:
            stopProcess = True
            return False
        counts[behavior] += 1
        totalCount += 1
        return True
    def fromMessages(c):
        for message in c['messages']:
            variations = getVariations(message)
            for variation in variations:
                
                if stopProcess:
                    return
                if not addToCount(behavior):
                    break
                addComment(c,variation)

    for c in searchIn:
        behavior = c['behavior']
        if 'tags' in c and exclude_tags:
            skipMessage = False
            for tag in  c['tags']:
                if tag in exclude_tags:
                    skipMessage = True
            if skipMessage:
                continue
        if stopProcess:
            break
        if 'message' in c:
            if addToCount(behavior):
                addComment(c)
        elif 'messages' in c:
            fromMessages(c)
            continue
        else:
            raise Exception(f"Unknown comment type: {c}")
    if timestamps:
        intervals = int((timestamps[1] - timestamps[0]) / len(comments))
        actPart = timestamps[0]
        for x in comments:
            x['timestamp'] = actPart
            actPart += intervals
    if seed:
        random.seed(seed)
    random.shuffle(comments)
    return comments
        
            

def getCombinations(text:str):
    replacers = [re.findall(MATCH_VARIATIONS,x) for x in re.findall(MATCH_POSITIONS, text)]
    return list(itertools.product(*replacers))

def getVariations(text:str,combinations = None):
    combinations =getCombinations(text) if combinations is None else combinations
    texts = []
    for combination in combinations:
        variation = text
        toReplace = re.findall(MATCH_FULL_POSITIONS, text)
        for i in range(len(combination)):
            variation = variation.replace(f"{toReplace[i]}",combination[i])
        texts.append(variation)
    return texts

def makeCSV(outFile:str,config:dict = {'limit':100},useData = commentsData):
    import csv
    data = makeData(**config,searchIn=useData)
    fieldnames = ['message', 'type', 'origin']
    if 'timestamps' in config:
        fieldnames.append('timestamp')
    with open(outFile, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            del row['expected']
            writer.writerow(row)