import * as React from 'react';
import * as d3 from 'd3';
// import manURL from '../assets/man.png';
// import womanURL from '../assets/woman.png';
import guanURL from '../assets/guan.png';
import widthURL from '../assets/width.png';
import radiusURL from '../assets/radius.png';
import { Switch } from 'antd';

type tree = {
    id: number,
    [propName: string]: any,
}


interface Props {
    graph: tree,
    [propName: string]: any;
}

class PTargetTree extends React.Component<Props, any>{
    private svgRef: React.RefObject<SVGSVGElement>;
    private svgWidth: number = 0;
    private svgHeight: number = 0;
    private padding = { top: 10, bottom: 10, left: 20, right: 20 };
    private circleR_min = 6;
    private circleR_max = 15;
    private lineWidthMin: number = 1;
    private lineWidthMax: number = 5;
    // private color = d3.schemePaired;
    private color = ["#fbb4ae", "#b3cde3", "#ccebc5", "#decbe4", "#fed9a6", "#ffffcc", "#e5d8bd", "#fddaec", "#f2f2f2", "#e41a1c"];
    constructor(props: Props) {
        super(props);
        this.svgRef = React.createRef();
        this.state = { layOutNodes: [], layOutLinks: [], focusNode: {} ,switch:true,};
        this.switch = this.switch.bind(this);
    }
    treeLayout(tree: tree, height: number, width: number): void {

        let maxAge = this.getMaxAge(tree);
        let minAge = this.getMinAge(tree);
        let maxYear = this.getMaxYear(tree);
        let minYear = this.getMinYear(tree);

        width = width - this.padding.left - 20;
        height = height - this.padding.top - 30;
        let YearScale = d3.scaleLinear().domain([minYear as unknown as any, maxYear as unknown as any]).range([this.padding.left, width]);
        let AgeScale = d3.scaleLinear().domain([minAge, maxAge as unknown as any]).range([this.circleR_min, this.circleR_max]);
        let xAxis = d3.axisBottom(YearScale);
        d3.select("#svg_pTargetTree" + this.props.graph.id)
            .select(".axis")
            .selectAll("g")
            .remove()
        d3.select("#svg_pTargetTree" + this.props.graph.id)
            .select(".axis")
            .append("g")
            .attr("transform", `translate(0,${height})`)
            .call(xAxis)

        var maxChildrenCount = 0;
        if (tree.children) {
            for (let i = 0; i < tree.children.length; i++) {
                let c = this.getNodeChildrenCount(tree.children[i])
                if (c > maxChildrenCount)
                    maxChildrenCount = c;
            }
        }
        else {
            maxChildrenCount = 0;
        };

        var lineWidthScale = d3.scaleLinear().domain([0, maxChildrenCount])
            .range([this.lineWidthMin, this.lineWidthMax]);

        let treeData = d3.tree().size([height, width])(d3.hierarchy(tree));

        let treeDataNodes = treeData.descendants();
        let treeNodesDic: { [propName: string]: any } = {};

        treeDataNodes.forEach((d: any) => {
            if ('id' in d.data)
                treeNodesDic[d.data.id] = d;
            else
                treeNodesDic[d.data.name] = d;
            if (d.data.birthyear === "-99" || d.data.birthyear === "-98") {
                d.r = this.circleR_min;
                let ty = d.y;
                if (!d.parent && d.children) {//根节点且有孩子
                    let childMinBiryear = this.getChildrenMinBirthyear(d);
                    if (childMinBiryear === 10000)
                        ty = d.y
                    else ty = YearScale(childMinBiryear);
                }
                else if (!d.parent && !d.children) {//单独一个根节点
                    ty = d.y;
                }
                else if (d.parent && !d.children) {//有父亲没孩子
                    if (d.parent.data.birthyear === '-99' || d.parent.data.birthyear === '-98') {
                        let brotherMinBirthyear = this.getBrotherMinBirthyear(d);
                        if (brotherMinBirthyear === 10000) {//如果兄弟出生年都未知
                            ty = d.y;
                        }
                        else
                            ty = YearScale(brotherMinBirthyear as unknown as any);
                    }
                    else {
                        ty = YearScale(Number(d.parent.data.birthyear) + 15);
                    }
                }
                else if (d.parent && d.children) {//有父亲有孩子
                    let childMinBiryear = this.getChildrenMinBirthyear(d);
                    if (d.parent.data.birthyear === '-99' || d.parent.data.birthyear === '-98') {//父亲出生年未知
                        let brotherMinBiryear = this.getBrotherMinBirthyear(d);
                        if (childMinBiryear === 10000 && brotherMinBiryear === 10000) {//孩子出生年都未知
                            ty = d.y;
                        }
                        else if (childMinBiryear === 10000 && brotherMinBiryear !== 10000) {
                            ty = YearScale(brotherMinBiryear as unknown as any)
                        }
                        else if (childMinBiryear !== 10000 && brotherMinBiryear === 10000) {
                            ty = YearScale(childMinBiryear - 20);
                        }
                        else {
                            ty = YearScale(childMinBiryear - 20);
                        }
                    }
                    else {//父亲出生年已知
                        if (childMinBiryear === 10000)
                            ty = YearScale(Number(d.parent.data.birthyear) + 15);
                        else ty = YearScale((childMinBiryear + Number(d.parent.data.birthyear)) / 2);
                    }
                }
                d.y = ty;
                // return `translate(${ty},${d.x})`;
            }

            else {
                d.r = AgeScale(Number(d.data.age))
                d.y = YearScale(Number(d.data.birthyear));
            }
            if (!d.parent && d.x < this.svgHeight / 2) {
                d.x = this.svgHeight / 2;
            }
            // return `translate(${YearScale(d.data.birthyear)},${d.x})`;
        })

        let treeDataLinks = treeData.links();
        let createLink = d3.linkHorizontal()  //d3.linkVertical()  d3.linkHorizontal().x(d => d.y).y(d => d.x)
            .x((d: any) => {
                if (d.data.birthyear === "-99" || d.data.birthyear === "-98") {
                    if (!d.parent && d.children) {//根节点且有孩子
                        let childMinBiryear = this.getChildrenMinBirthyear(d);
                        if (childMinBiryear === 10000)
                            return d.y
                        else return YearScale(childMinBiryear);
                    }
                    else if (!d.parent && !d.children) {//单独一个根节点
                        return d.y;
                    }
                    else if (d.parent && !d.children) {//有父亲没孩子
                        if (d.parent.data.birthyear === '-99' || d.parent.data.birthyear === '-98') {
                            let brotherMinBirthyear = this.getBrotherMinBirthyear(d);
                            if (brotherMinBirthyear === 10000) {//如果兄弟出生年都未知
                                return d.y;
                            }
                            else
                                return YearScale(brotherMinBirthyear as unknown as any);
                        }
                        else {
                            return YearScale(Number(d.parent.data.birthyear) + 15);
                        }
                    }
                    else if (d.parent && d.children) {//有父亲有孩子
                        let childMinBiryear = this.getChildrenMinBirthyear(d);
                        if (d.parent.data.birthyear === '-99' || d.parent.data.birthyear === '-98') {//父亲出生年未知
                            let brotherMinBiryear = this.getBrotherMinBirthyear(d);
                            if (childMinBiryear === 10000 && brotherMinBiryear === 10000) {//孩子出生年都未知
                                return d.y;
                            }
                            else if (childMinBiryear === 10000 && brotherMinBiryear !== 10000) {
                                return YearScale(brotherMinBiryear as unknown as any)
                            }
                            else if (childMinBiryear !== 10000 && brotherMinBiryear === 10000) {
                                return YearScale(childMinBiryear - 20);
                            }
                            else {
                                return YearScale(childMinBiryear - 20);
                            }
                        }
                        else {//父亲出生年已知
                            if (childMinBiryear === 10000)
                                return YearScale(Number(d.parent.data.birthyear) + 15);
                            else return YearScale((childMinBiryear + Number(d.parent.data.birthyear)) / 2);
                        }
                    }

                }
                else return YearScale(Number(d.data.birthyear));
            })
            .y((d: any) => {
                if (!d.parent && d.x < this.svgHeight / 2)
                    return this.svgHeight / 2;
                else
                    return d.x
            })

        treeDataLinks.forEach((value: any) => {
            value.d = createLink(value);
            value.width = lineWidthScale(this.getNodeChildrenCount(treeNodesDic[value.target.data.id ? value.target.data.id : value.target.data.name]));
        })


        this.setState({ layOutNodes: treeDataNodes, layOutLinks: treeDataLinks });
    }
    treeLayout2(tree: tree, height: number, width: number) {
        width = width - this.padding.left - 20;
        height = height - this.padding.top - 30;
        d3.select("#svg_pTargetTree" + this.props.graph.id)
            .select(".axis")
            .selectAll("g")
            .remove()

        let treeData = d3.tree().size([height, width])(d3.hierarchy(tree));

        let treeDataNodes = treeData.descendants();
        treeDataNodes.forEach((d: any) => {
            d.r = this.circleR_min;
            d.y= d.y+this.padding.left;
            if (!d.parent && d.x < this.svgHeight / 2)
                d.x=this.svgHeight / 2;
        })

        let treeDataLinks = treeData.links();
        let createLink = d3.linkHorizontal()  //d3.linkVertical()  d3.linkHorizontal().x(d => d.y).y(d => d.x)
            .x((d: any) => {
                return d.y;
            })
            .y((d: any) => {
                if (!d.parent && d.x < this.svgHeight / 2)
                    return this.svgHeight / 2;
                else
                    return d.x
            })

        treeDataLinks.forEach((value: any) => {
            value.d = createLink(value);
        })


        this.setState({ layOutNodes: treeDataNodes, layOutLinks: treeDataLinks });
    }
    getChildrenMinBirthyear(d: any): number {//获得孩子节点中的最小出生年
        let childMinBiryear = d3.min(d.children, (data: any) => {
            if (data.data.birthyear === '-99' || data.data.birthyear === '-98')
                return 10000;
            return Number(data.data.birthyear)
        });
        return childMinBiryear as unknown as any;
    }

    getBrotherMinBirthyear(d: any) {
        let brotherMinBirthyear = d3.min(d.parent.children, (data: any) => {
            if (data.data.birthyear === '-99' || data.data.birthyear === '-98')
                return 10000;
            return Number(data.data.birthyear)
        });
        return brotherMinBirthyear;
    }
    getMaxAge(tree: tree) {
        var age = Number(tree.age);
        if (tree.hasOwnProperty("children")) {
            for (var i = 0; i < tree.children.length; i++) {
                age = d3.max([age, this.getMaxAge(tree.children[i]) as unknown as any]);
            }
            return age;
        }
        else {
            return d3.max([age, -99]);
        }
    }
    getMinAge(tree: tree) {
        var age = Number(tree.age) === -99 ? 1000 : Number(tree.age) as unknown as any;
        if (tree.hasOwnProperty("children")) {
            for (var i = 0; i < tree.children.length; i++) {
                age = d3.min([age, this.getMinAge(tree.children[i])]);
            }
            return age;
        }
        else {
            return age;
        }
    }
    getMaxYear(tree: tree) {
        var year = Number(tree.birthyear);
        if (tree.hasOwnProperty("children")) {
            for (var i = 0; i < tree.children.length; i++) {
                year = d3.max([year, this.getMaxYear(tree.children[i]) as unknown as any]);
            }
            return year;
        }
        else {
            return d3.max([year, -99]);
        }
    }
    getMinYear(tree: tree) {
        var year = Number(tree.birthyear) === -99 ? 10000 : Number(tree.birthyear);
        if (year === -98) {
            year = 10000;
        }
        if (tree.hasOwnProperty("children")) {
            for (var i = 0; i < tree.children.length; i++) {
                year = d3.min([year, this.getMinYear(tree.children[i]) as unknown as any]);
            }
            return year;
        }
        else {
            return d3.min([year, 10000]);
        }
    }
    getNodeChildrenCount(d: any) {//获得该节点的所有后代数量
        let count = 0;
        if (d.children) {
            for (let i = 0; i < d.children.length; i++) {
                count += this.getNodeChildrenCount(d.children[i]) + 1;
            }
            return count;
        }
        else {
            return 0;
        }
    }
    mouseOver(data: any): void {
        console.log(data);
    }
    switch(value: boolean) {
        if (value === false) {
            this.treeLayout2(this.props.graph, this.svgHeight, this.svgWidth);
            this.setState({switch:false})
        }
        else {
            this.treeLayout(this.props.graph, this.svgHeight, this.svgWidth);
            this.setState({switch:true})
        }
    }
    componentDidMount(): void {
        this.svgWidth = this.svgRef.current?.clientWidth || 0;
        this.svgHeight = this.svgRef.current?.clientHeight || 0;
        this.treeLayout(this.props.graph, this.svgHeight, this.svgWidth);
        let svg = d3.select('#svg_pTargetTree' + this.props.graph.id)
        svg.call(d3.zoom()
            .scaleExtent([0.1, 7])
            .on("zoom", zoomed.bind(this)) as unknown as any);
        // let height=this.svgHeight - this.padding.top - 30;

        function zoomed() {
            let transform = d3.zoomTransform(svg.node() as unknown as Element);
            // let y=transform.y+ height;
            //svg_point.selectAll("circle").attr("r",1);
            svg.selectAll(".pTargetTree").attr("transform", "translate(" + transform.x + "," + transform.y + ") scale(" + transform.k + ")");
            // svg.selectAll(".axis").attr("transform", "translate(" + transform.x + "," + y + ") scale(" + transform.k + ")");
        }
    }
    componentWillReceiveProps(nextProps: Props): void {
        if(this.state.switch===true){
            this.treeLayout(nextProps.graph, this.svgHeight, this.svgWidth);
        }
        else{
            this.treeLayout2(nextProps.graph, this.svgHeight, this.svgWidth);
        }
    }
    render(): React.ReactElement {
        // console.log(this.state.layOutNodes)
        const { layOutNodes, layOutLinks } = this.state;
        let villageNum: Array<string> = [];
        let villageFlag: Array<React.ReactElement> = [];
        let icons: Array<React.ReactElement> = [];
        let nodes = null;
        nodes = layOutNodes.map((value: any, index: number) => {
            let colorIndex = 0;
            // if (value.data.village !== "-99") {
            colorIndex = villageNum.indexOf(value.data.village);
            if (colorIndex < 0) {
                colorIndex = villageNum.length;
                villageFlag.push(<rect fill={this.color[colorIndex]} key={colorIndex} x={this.svgWidth - (10 - colorIndex) * 10 - 10} y={this.svgHeight - 15} width={10} height={10}></rect>)
                villageNum.push(value.data.village);
            }
            // }
            // let villageColor = value.data.village === "-99" ? "#ccc" : this.color[colorIndex];
            let villageColor = this.color[colorIndex];

            // console.log(value.data.sex);
            if (value.data.sex === "2" || ((value.data.sex === "-99" || value.data.sex === "-98") && value.children)) {
                if (value.data.guan !== "0" && value.data.guan !== "-99" && value.data.guan !== "-98")
                    icons.push(<image style={{transition:'all 0.5s ease'}} key={index} x={value.y - value.r / 2} y={value.x - value.r / 2} width={value.r} height={value.r} xlinkHref={guanURL}></image>)
                return <rect style={{transition:'all 0.5s ease'}} x={value.y - value.r} y={value.x - value.r} width={value.r * 2} height={value.r * 2} key={index} fill={villageColor} strokeWidth="1px"></rect>
            }



            // icons.push(<image key={index} x={value.y - value.r / 2} y={value.x - value.r/2} width={value.r} height={value.r} xlinkHref={womanURL}></image>)

            else {
                return <circle style={{transition:'all 0.5s ease'}} r={value.r} cx={value.y} cy={value.x} key={index} fill={villageColor} strokeWidth="1px" stroke="white"
                    cursor='pointer'></circle>
            }

            // return <circle onMouseOver={this.mouseOver.bind(this, value.data)} r={value.r} cx={value.y} cy={value.x} key={index} fill={villageColor} strokeWidth="1px" stroke="white"
            //     cursor='pointer'></circle>
        })


        let links = layOutLinks.map((value: any, index: number) => {
            return <path style={{transition:'all 0.5s ease'}} d={value.d} fill="none" strokeWidth={value.width} stroke="#ccc" key={index}></path>
        })
        return (
            <div style={{ width: '100%', height: '100%', position: 'relative' }}>
                <Switch className="treeSwitch" defaultChecked size="small" style={{ position: 'absolute', right: '15px', top: '5px' }} onChange={this.switch} />
                <svg id={"svg_pTargetTree" + this.props.graph.id} ref={this.svgRef} style={{ width: '100%', height: '100%'}} onClick={this.props.onClick ? this.props.onClick.bind(this.props.parent, this.props.graph) : null}>
                    <text x={this.svgWidth-this.padding.right-70} y={15} fontSize="10px">Layout</text>
                    <g className="pTargetTree" transform='translate(0,0)'>{links}</g>
                    <g className="pTargetTree" transform='translate(0,0)'>{nodes}</g>
                    <g className="pTargetTree">{icons}</g>
                    {villageFlag}

                    <text x={this.svgWidth - 10 * 10 - 10 - 8 * 5} y={this.svgHeight - 7} fontSize="10px">Village:</text>
                    <text x={2} y={this.svgHeight - 7} fontSize="10px">Male:</text>
                    {/* <image x={30} y={this.svgHeight - 15} width={10} height={10} xlinkHref={manURL}></image> */}
                    <rect x={30} y={this.svgHeight - 15} width={10} height={10} fill="#ccc"></rect>
                    <text x={50} y={this.svgHeight - 7} fontSize="10px">Female:</text>
                    {/* <image x={89} y={this.svgHeight - 15} width={10} height={10} xlinkHref={womanURL}></image> */}
                    <circle cx={94} cy={this.svgHeight - 10} r={5} fill="#ccc"></circle>
                    <text x={115} y={this.svgHeight - 7} fontSize="10px">Officer:</text>
                    <rect x={152} y={this.svgHeight - 15} width={10} height={10} fill="#ccc"></rect>
                    <image x={152} y={this.svgHeight - 15} width={8} height={8} xlinkHref={guanURL}></image>
                    <text x={177} y={this.svgHeight - 7} fontSize="10px">Progeny Size:</text>
                    <image x={245} y={this.svgHeight - 25} width={30} height={30} xlinkHref={widthURL}></image>
                    <text x={290} y={this.svgHeight - 7} fontSize="10px">Life Time:</text>
                    <image x={340} y={this.svgHeight - 18} width={15} height={15} xlinkHref={radiusURL}></image>

                    <g className="axis"></g>
                </svg>
            </div>

        )
    }
}

export default PTargetTree;