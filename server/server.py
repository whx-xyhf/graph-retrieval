from flask import Flask, render_template, request, jsonify,make_response
import json
import math
import numpy as np
from dataProcessing.Ged import getGed
from dataProcessing.getCCATsne import reTsne
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from dataProcessing.graph2vec import WeisfeilerLehmanMachine
from dataProcessing.getdbscan import runDBSCAN,reDBSCAN
import networkx as nx
import os
import time

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
time_interval=1

@app.after_request
def cors(environ):
    environ.headers['Access-Control-Allow-Origin']='*'
    environ.headers['Access-Control-Allow-Method']='*'
    environ.headers['Access-Control-Allow-Headers']='x-requested-with,content-type'
    return environ

@app.route("/",methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        dimensions = str(request.get_json()['dimensions'])
        strWeight=str(request.get_json()['strWeight'])
        attrWeight = str(request.get_json()['attrWeight'])
        attrChecked=request.get_json()['attrChecked']
        dataType=request.get_json()['dataType']

        with open('./dataProcessing/data/'+dataType+'/subGraphs_'+str(time_interval)+'.json','r') as fr:
            data=json.load(fr)
        attrStr = ''
        for i in data[0]['attr']:
            if {'name':i,'value':True} in attrChecked:
                attrStr+='1'
            else:
                attrStr+='0'
        print(attrStr)
        with open('./dataProcessing/data/'+dataType+'/vectors2d_'+str(time_interval)+'_'+dimensions+'_'+strWeight+'_'+attrWeight+'_'+attrStr+'.json','r') as fr:
            vectors=json.load(fr)
        with open('./dataProcessing/data/'+dataType+'/dbscanParameter.json','r') as fr:
            parameter=json.load(fr)
            for i in parameter:
                if i['dimensions']==int(dimensions) and i['strWeight']==int(strWeight) and i['attrWeight']==int(attrWeight) and i['attrStr']==attrStr:
                    eps=i['eps']
                    min_samples=i['min_samples']

        for i in range(len(data)):
            data[i]['x']=float(vectors[str(data[i]['id'])]['x'])
            data[i]['y']=float(vectors[str(data[i]['id'])]['y'])
            data[i]['cluster']=vectors[str(data[i]['id'])]['cluster']
        res = make_response(jsonify({'code': 200, "data": data,'eps':eps,'minSamples':min_samples}))
    return res

@app.route("/searchPerson",methods = ['POST', 'GET'])
def search():#根据关键字匹配人名
    if request.method == 'POST':
        resData={}
        dataType = request.get_json()['dataType']
        with open('./dataProcessing/data/'+dataType+'/node2Num.json','r') as fr:
            data=json.load(fr)
            wd=request.get_json()['wd']
            if wd=="":
                res = make_response(jsonify({'code': 200, "data": data}))
            else:
                for key in data:
                    if key.lower().find(wd.lower())>=0:
                        resData[key]=data[key]
                res = make_response(jsonify({'code': 200, "data": resData}))
    return res

@app.route("/searchGraphByPersonId",methods = ['POST', 'GET'])
def searchGraphByPersonId():#根据人id搜索包含该人的网络
    if request.method == 'POST':
        resData=[]
        num2node={}
        strWeight = str(request.get_json()['strWeight'])
        attrWeight = str(request.get_json()['attrWeight'])
        wd = int(request.get_json()['wd'])  # 该人的id
        dimensions = str(request.get_json()['dimensions'])
        attrChecked = request.get_json()['attrChecked']
        dataType = request.get_json()['dataType']
        if dataType=='Author':
            with open('./dataProcessing/data/'+dataType+'/node2Num.json','r') as fr:
                node2Num=json.load(fr)#{www:1}
                for key in node2Num:
                    num2node[node2Num[key]]=key#{1:www}
        with open('./dataProcessing/data/'+dataType+'/subGraphs_'+str(time_interval)+'.json','r') as fr:
            data=json.load(fr)
        attrStr = ''
        for i in data[0]['attr']:
            if {'name': i, 'value': True} in attrChecked:
                attrStr += '1'
            else:
                attrStr += '0'
        with open('./dataProcessing/data/'+dataType+'/vectors2d_' + str(
                time_interval) + '_' + dimensions + '_' + strWeight + '_' + attrWeight + '_' +attrStr+'.json', 'r') as fr:
            vectors = json.load(fr)
            #遍历所有子图，如果子图点集中包含搜索的点则加入返回数据中
            if dataType == 'Author':
                for graph in data:
                    if graph['nodes'].count(wd)>0:
                        # nodeName={}
                        # for i in graph['nodes']:
                        #     nodeName[i]=num2node[i]
                        # graph['names']=nodeName
                        graph['x']=float(vectors[str(graph['id'])]['x'])
                        graph['y']=float(vectors[str(graph['id'])]['y'])
                        resData.append(graph)
            elif dataType=='Family':
                for graph in data:
                    if graph['nodes'].count(wd)>0:
                        graph['x']=float(vectors[str(graph['id'])]['x'])
                        graph['y']=float(vectors[str(graph['id'])]['y'])
                        resData.append(graph)
            res = make_response(jsonify({'code': 200, "data": resData}))
    return res

@app.route("/searchGraphByGraphId",methods = ['POST', 'GET'])
def searchGraphByGraphId():#根据图id搜索该图
    if request.method == 'POST':
        resData=[]
        num2node={}
        strWeight = str(request.get_json()['strWeight'])
        attrWeight = str(request.get_json()['attrWeight'])
        wd = int(request.get_json()['wd'])  # 该图的id
        dimensions = str(request.get_json()['dimensions'])
        attrChecked = request.get_json()['attrChecked']
        dataType = request.get_json()['dataType']
        if dataType == 'Author':
            with open('./dataProcessing/data/'+dataType+'/node2Num.json','r') as fr:
                node2Num=json.load(fr)#{www:1}
                for key in node2Num:
                    num2node[node2Num[key]]=key#{1:www}
        with open('./dataProcessing/data/'+dataType+'/subGraphs_'+str(time_interval)+'.json','r') as fr:
            data=json.load(fr)
        attrStr = ''
        for i in data[0]['attr']:
            if {'name': i, 'value': True} in attrChecked:
                attrStr += '1'
            else:
                attrStr += '0'
        with open('./dataProcessing/data/'+dataType+'/vectors2d_' + str(
                time_interval) + '_' + dimensions + '_' + strWeight + '_' + attrWeight + '_'+attrStr +'.json', 'r') as fr:
            vectors = json.load(fr)
            for graph in data:
                if graph['id']==wd:
                    # if dataType == 'Author':
                    #     nodeName = {}
                    #     for i in graph['nodes']:
                    #         nodeName[i] = num2node[i]
                    #     graph['names'] = nodeName
                    graph['x'] = float(vectors[str(graph['id'])]['x'])
                    graph['y'] = float(vectors[str(graph['id'])]['y'])
                    graph['cluster'] = vectors[str(graph['id'])]['cluster']
                    resData.append(graph)
                    break
            res = make_response(jsonify({'code': 200, "data": resData}))
    return res

@app.route("/matchGraph",methods = ['POST', 'GET'])
def match():#匹配相似图
    if request.method == 'POST':
        sourceGraph = request.get_json()['wd']#要匹配的图
        num=int(request.get_json()['num'])
        dimensions = str(request.get_json()['dimensions'])
        strWeight = str(request.get_json()['strWeight'])
        attrWeight = str(request.get_json()['attrWeight'])
        attrChecked = request.get_json()['attrChecked']
        attrRange = request.get_json()['attrValue']
        dataType = request.get_json()['dataType']
        attrValue = {}
        for key in attrRange:
            attrValue[key] = int((attrRange[key][0] + attrRange[key][1]) / 2)
        resData=[]

        with open('./dataProcessing/data/'+dataType+'/subGraphs_'+str(time_interval)+'.json','r') as fr:
            data=json.load(fr)
        attrStr = ''
        useAttr = []
        for i in data[0]['attr']:
            if {'name': i, 'value': True} in attrChecked:
                attrStr += '1'
                useAttr.append(i)
            else:
                attrStr += '0'
        with open('./dataProcessing/data/'+dataType+'/vectors2d_' + str(
                time_interval) + '_' + dimensions + '_' + strWeight + '_' + attrWeight + '_' +attrStr+ '.json', 'r') as fr:
            vectors = json.load(fr)
            for i in range(len(data)):
                if data[i]['id']!=sourceGraph['id']:
                    flag = True
                    if attrWeight != 0:
                        for key in useAttr:
                            if data[i]['attr'][key] < attrRange[key][0] or data[i]['attr'][key] > attrRange[key][1]:
                                flag = False
                                break
                    if flag:
                        data[i]['x'] = float(vectors[str(data[i]['id'])]['x'])
                        data[i]['y'] = float(vectors[str(data[i]['id'])]['y'])
                        data[i]['cluster'] = vectors[str(data[i]['id'])]['cluster']
                        distance=math.pow(float(vectors[str(sourceGraph['id'])]['x'])-data[i]['x'],2)+math.pow(float(vectors[str(sourceGraph['id'])]['y'])-data[i]['y'],2)
                        data[i]['distance']=distance
                    else:
                        data[i]['distance'] = float('inf')
                    resData.append(data[i])
            resData=sorted(resData,key=lambda x:x['distance'])#sort(key=lambda x:x["distance"])
            res = make_response(jsonify({'code': 200, "data": resData[:num]}))
        file = './dataProcessing/data/' + dataType + '/' + 'historyRecord' + str(time_interval) + '.json'
        date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        oneRecord = {'graph': sourceGraph, 'dimensions': dimensions, 'attrChecked': attrChecked,'date':date,'strWeight':strWeight,'attrWeight':attrWeight}
        if os.path.exists(file):
            with open(file, 'r') as fr:
                record = json.load(fr)
            record.insert(0, oneRecord)
            with open(file, 'w') as fw:
                json.dump(record,fw)
        else:
            with open(file, 'w') as fw:
                json.dump([oneRecord],fw)
    return res

@app.route("/getAttr",methods = ['POST', 'GET'])
def getAttr():
    if request.method == 'POST':
        dataType = request.get_json()['dataType']
        with open('./dataProcessing/data/'+dataType+'/subGraphs_'+str(time_interval)+'.json','r') as fr:
            data=json.load(fr)
            attr=[]
            for i in data:
                attr.append({'id':i['id'],'attr':i['attr'],'str':i['str']})
            res = make_response(jsonify({'code': 200, "data": attr}))
    return res

@app.route("/matchModel",methods = ['POST', 'GET'])
def matchModel():
    if request.method == 'POST':
        features= request.get_json()['features']
        features_={}
        for i in features:
            features_[int(i)]=features[i]
        edges = request.get_json()['edges']
        nodes = request.get_json()['nodes']
        name=request.get_json()['name']
        strWeight = request.get_json()['strWeight']
        attrWeight = request.get_json()['attrWeight']
        dimensions = str(request.get_json()['dimensions'])
        attrChecked = request.get_json()['attrChecked']
        num = request.get_json()['num']
        attrRange=request.get_json()['attrValue']
        dataType = request.get_json()['dataType']

        attrValue={}
        attrValue_={}
        for key in attrRange:
            attrValue[key]=int((int(attrRange[key][0])+int(attrRange[key][1]))/2)
            attrValue_[key] = int((int(attrRange[key][0]) + int(attrRange[key][1])) / 2)
        graph=nx.from_edgelist(edges)
        machine = WeisfeilerLehmanMachine(graph, features_, 2)
        doc = TaggedDocument(words=machine.extracted_features, tags=["g_" + name])
        doc = machine.extracted_features
        model = Doc2Vec.load('./dataProcessing/data/'+dataType+'/Graph2vec_'+dimensions+'.model')
        docVectors = model.infer_vector(doc, epochs=100)
        docVectors=docVectors.tolist()

        with open('./dataProcessing/data/'+dataType+'/attrMeanStd_'+str(time_interval)+'.json','r') as fr:
            mean_std=json.load(fr)
            for key in attrValue:
                attrValue[key]=(attrValue[key]-mean_std['min'][key])/(mean_std['max'][key]-mean_std['min'][key])

        with open('./dataProcessing/data/'+dataType+'/subGraphs_'+str(time_interval)+'.json','r') as fr:
            data=json.load(fr)
        attrStr = ''
        attrVector = []
        useAttr=[]
        for i in data[0]['attr']:
            if {'name': i, 'value': True} in attrChecked:
                attrVector.append(attrValue[i])
                attrStr += '1'
                useAttr.append(i)
            else:
                attrStr += '0'
                attrVector.append(0)

        dimensionsAttr=len(attrStr)
        dimensionsStr=int(dimensions)

        with open('./dataProcessing/data/'+dataType+'/dbscanParameter.json', 'r') as fr:
            parameter = json.load(fr)
            for p in parameter:
                if p['dimensions'] == dimensions and p['strWeight'] == strWeight and p['attrWeight'] == attrWeight and p[
                    'attrStr'] == attrStr:
                    eps=p['eps']
                    minSamples=p['min_samples']
                    break

        file='./dataProcessing/data/'+dataType+'/'+ 'vectors2d_' + str(time_interval) + '_' + str(dimensionsStr) + '_' + str(
                    strWeight) + '_' + str(attrWeight) + '_' + attrStr +'model'+name+ '.json'
        if os.path.exists(file):
            with open(file,'r') as fr:
                Data=json.load(fr)
            dataSet=[]
            ids=[]
            for i in Data:
                dataSet.append([float(data[i]['x']), float(data[i]['y'])])
                ids.append(i)
            tsneData,dic=reDBSCAN(dataSet, id, eps,minSamples)
            with open('./dataProcessing/data/'+dataType+'/' + 'cluster_points_' + str(time_interval) + '_' + str(dimensionsStr) + '_' + str(
                    strWeight) + '_' + str(attrWeight) + '_' + attrStr + 'model' + '.json',
                      'w') as fw:  # 每个标签有哪些点
                json.dump(dic, fw)
        else:
            tsneData=reTsne(name,docVectors,attrVector,dirPath = './dataProcessing/data/'+dataType+'/',dimensionsStr=dimensionsStr,dimensionsAttrChecked=attrStr
                       ,strWeight=strWeight,attrWeight=attrWeight,eps=eps,min_samples=minSamples,saveFile=True)

        newData=[]
        for i in range(len(data)):
            data[i]['x']=float(tsneData[str(data[i]['id'])]['x'])
            data[i]['y']=float(tsneData[str(data[i]['id'])]['y'])
            data[i]['cluster'] = tsneData[str(data[i]['id'])]['cluster']
            data[i]['distance']=math.pow(data[i]['x']-float(tsneData[name]['x']),2)+math.pow(data[i]['y']-float(tsneData[name]['y']),2)
            newData.append(data[i])
        centerPoint={'id':int(name),'nodes':nodes,'edges':edges,'attr':attrValue_,'x':float(tsneData[name]['x']),'y':float(tsneData[name]['y']),'distance':100000}
        newData.append(centerPoint)
        newData=sorted(newData,key=lambda x:x['distance'])
        res = make_response(jsonify({'code': 200, "all": newData,'match':newData[:num],'center':centerPoint}))

    return res

@app.route("/readHistoryRecord",methods = ['POST', 'GET'])
def readHistoryRecord():
    if request.method == 'POST':
        dimensions = str(request.get_json()['dimensions'])
        attrChecked = request.get_json()['attrChecked']
        dataType = request.get_json()['dataType']
        strWeight = str(request.get_json()['strWeight'])
        attrWeight = str(request.get_json()['attrWeight'])
        resData=[]
        file = './dataProcessing/data/' + dataType + '/' + 'historyRecord' + str(time_interval) + '.json'
        with open(file,'r') as fr:
            data=json.load(fr)
        for i in data:
            if i['dimensions']==dimensions and i['attrChecked']==attrChecked and i['strWeight']==strWeight and i['attrWeight']==attrWeight:
                resData.append({'graph':i['graph'],'date':i['date']})
        res = make_response(jsonify({'code': 200, 'data':resData}))
    return res

@app.route("/getCluster",methods = ['POST', 'GET'])
def getCluster():
    if request.method == 'POST':
        dimensions = str(request.get_json()['dimensions'])
        attrChecked = request.get_json()['attrChecked']
        dataType = request.get_json()['dataType']
        strWeight = request.get_json()['strWeight']
        attrWeight = request.get_json()['attrWeight']
        cluster=str(request.get_json()['cluster'])
        with open('./dataProcessing/data/'+dataType+'/subGraphs_'+str(time_interval)+'.json','r') as fr:
            data=json.load(fr)
        attrStr = ''
        for i in data[0]['attr']:
            if {'name': i, 'value': True} in attrChecked:
                attrStr += '1'
            else:
                attrStr += '0'
        with open('./dataProcessing/data/'+dataType+'/'+ 'cluster_points_' + str(time_interval) + '_' + str(dimensions) + '_' + str(
                    strWeight) + '_' + str(attrWeight) + '_' + attrStr + '.json','r') as fr:
            clusterData=json.load(fr)
            ids=clusterData[cluster]
        with open('./dataProcessing/data/'+dataType+'/vectors2d_' + str(
                time_interval) + '_' + str(dimensions) + '_' + str(strWeight) + '_' + str(attrWeight) + '_' +attrStr+ '.json', 'r') as fr:
            vectors = json.load(fr)
        centerx=0
        centery=0
        for i in ids:
            centerx+=float(vectors[i]['x'])
            centery+=float(vectors[i]['y'])
        centerx/=len(ids)
        centery/=len(ids)
        resData=[]
        for i in ids:
            resData.append({'id':i,'distance':math.pow(float(vectors[i]['x'])-centerx,2)+math.pow(float(vectors[i]['y'])-centery,2)})
        resData = sorted(resData, key=lambda x: x['distance'])
        res = make_response(jsonify({'code': 200, 'data': resData}))
    return res

@app.route("/reDbscan",methods = ['POST', 'GET'])
def reDbscan():
    if request.method == 'POST':
        dimensions = request.get_json()['dimensions']
        attrChecked = request.get_json()['attrChecked']
        dataType = request.get_json()['dataType']
        strWeight = request.get_json()['strWeight']
        attrWeight = request.get_json()['attrWeight']
        eps = request.get_json()['eps']
        minSamples=request.get_json()['minSamples']
        with open('./dataProcessing/data/' + dataType + '/subGraphs_' + str(time_interval) + '.json', 'r') as fr:
            data = json.load(fr)
        attrStr = ''
        for i in data[0]['attr']:
            if {'name': i, 'value': True} in attrChecked:
                attrStr += '1'
            else:
                attrStr += '0'
        vectors=runDBSCAN('./dataProcessing/data/' + dataType + '/',dimensions,strWeight,attrWeight,attrStr,eps,minSamples,time_interval)
        res = make_response(jsonify({'code': 200, "data": vectors}))
    return res



if __name__ == '__main__':
    app.run(host="0.0.0.0",
            port=8080)