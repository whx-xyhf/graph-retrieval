from sklearn.cluster import OPTICS
#聚类
import json
import matplotlib.pyplot as plt
import numpy as np
def loadDataSet(fileName):
    """
    输入：文件名
    输出：数据集
    描述：从文件读入数据集
    """
    dataSet = []
    ids=[]
    with open(fileName,'r') as fr:
        data=json.load(fr)
    for i in data:
        dataSet.append([float(data[i]['x']),float(data[i]['y'])])
        ids.append(i)
    return data,dataSet,ids

def plotFeature(data, clusters, clusterNum):
    nPoints = data.shape[1]
    matClusters = np.mat(clusters).transpose()
    fig = plt.figure()
    scatterColors = ['black', 'blue', 'green', 'yellow', 'red', 'purple', 'orange', 'brown']
    ax = fig.add_subplot(111)
    for i in range(clusterNum + 1):
        colorSytle = scatterColors[i % len(scatterColors)]
        subCluster = data[:, np.nonzero(matClusters[:, 0].A == i)]
        ax.scatter(subCluster[0, :].flatten().A[0], subCluster[1, :].flatten().A[0], c=colorSytle, s=1)

if __name__ == '__main__':
    print("正在进行dbscan聚类！！！")
    dirPath = './data/Author/'
    weight=[[1,1]]
    time_interval = 1
    dimensions = 128
    attrStr=['111111']
    for i in weight:
        for j in attrStr:
            data,points,ids=loadDataSet(dirPath+'vectors2d_'+str(time_interval)+'_'+str(dimensions)+'_'+str(i[0])+'_'+str(i[1])+'_'+j+'.json')
            clustering = OPTICS( min_samples=10).fit(points)
            labels = set(clustering.labels_)
            # pointsM=np.mat(points).transpose()
            # plotFeature(pointsM,clustering.labels_,len(labels))
            # plt.show()
            dic={}
            subGraphs=[]
            for label in labels:
                dic[str(label)]=[]
            index=0
            for label in clustering.labels_:
                dic[str(label)].append(ids[index])
                index+=1
            with open(dirPath+'cluster_points_'+str(time_interval)+'_'+str(dimensions)+'_'+str(i[0])+'_'+str(i[1])+'_'+j+'.json','w') as fw:#每个标签有哪些点
                json.dump(dic,fw)
            out = {}
            for k in range(len(ids)):
                out[ids[k]]={'id':ids[k],'cluster':int(clustering.labels_[k])}
            for k in data:
                data[k]['cluster']=out[k]['cluster']
            with open(dirPath+'vectors2d_'+str(time_interval)+'_'+str(dimensions)+'_'+str(i[0])+'_'+str(i[1])+'_'+j+'.json','w') as fw:
                json.dump(data,fw)

            print("聚类完成！！！")
            print("共"+str(len(labels))+"类")
            print(labels)

