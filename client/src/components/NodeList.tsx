import * as React from 'react';
import axios from 'axios'

interface Props{
    url:string;
    parent:any,
}

class NodeList extends React.Component<Props,any>{
    constructor(props:Props){
        super(props)
        this.state={wd:'',searchValue:{}}
        this.change=this.change.bind(this);
        this.search=this.search.bind(this);
        this.searchGraph=this.searchGraph.bind(this);
    }
    //input双向绑定
    change(e:React.ChangeEvent<HTMLInputElement>):void{
        this.setState({
            wd:e.target.value
        })
    }
    //搜索
    search():void{//根据搜索框的字段搜索作者
        axios.post(this.props.url+'/search',{wd:this.state.wd})
        .then(res=>{
            this.setState({searchValue:res.data.data});
        })
    }
    searchGraph(e:any):void{//根据名字搜索包含该节点的网络
        axios.post(this.props.url+'/searchGraph',{wd:e.target.dataset['num']})
        .then(res=>{
            // console.log(res.data.data);
            this.props.parent(res.data.data);
        })
    }
    componentDidMount():void{
        this.search();
    }
    render():React.ReactElement{
        let liList:Array<React.ReactElement>=[];
        for(let wd in this.state.searchValue){
            liList.push(
                <li data-num={this.state.searchValue[wd]} key={this.state.searchValue[wd]} onClick={this.searchGraph}>{wd}</li>
            )
        }
        return (
            <div className="nodeList">
                <input type="text" value={this.state.wd} onChange={(e:React.ChangeEvent<HTMLInputElement>)=>this.change(e)}></input>
                <input type="button" value="search" onClick={this.search}></input>
                {liList}
            </div>
        )
    }
}
export default NodeList