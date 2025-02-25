data = {'request_data':[['a',2],['b',521]]}
reqInfos = data['request_data']
def addReqInfo(data):
    if data['reqName'] == 'b':
        print('added')
        data['request_data'].append(['c', 123])
for nameData,valueData in reqInfos:
    data.update({'reqName':nameData,'reqValue':valueData})
    print(nameData)
    addReqInfo(data)
