var React = require('react');
var ReactDOM = require('react-dom');
var Infinite = require('react-infinite');

function Dish(props) {
    return (
        <div className="col-xs-12 col-md-4 col-lg-4">
            <a href={'/cookyourself/dish/' + props.link}>
                <img className="img-thumbnail post_picture" width="100%" height="100%"
                     src={props.url} alt="Dish"/></a>
            <h5 className="text-center">{props.name}</h5>
        </div>
    );
}

var ListItem = React.createClass({
    render: function () {
        return <div className="infinite-list-item">
            {/*<img src="http://images.media-allrecipes.com/userphotos/560x315/3606763.jpg" alt={this.props.num}/>*/}
            {/*<Dish name="Greek Lemon Chicken and Potatoes"*/}
            {/*url="http://images.media-allrecipes.com/userphotos/560x315/3606763.jpg" link="2"/>*/}
            {/*<Dish name="Greek Lemon Chicken and Potatoes"*/}
            {/*url="http://images.media-allrecipes.com/userphotos/560x315/3606763.jpg" link="2"/>*/}
            <Dish name={this.props.name1} url={this.props.url1} link={this.props.link1}/>
            <Dish name={this.props.name2} url={this.props.url2} link={this.props.link2}/>
            <Dish name={this.props.name3} url={this.props.url3} link={this.props.link3}/>
        </div>
    }
});

var dishes = [
    {
        name: 'Zucchini Brownies',
        url: 'http://images.media-allrecipes.com/userphotos/720x405/3837987.jpg',
        link: '2'
    },
    {
        name: 'Greek Lemon Chicken and Potatoes',
        url: 'http://images.media-allrecipes.com/userphotos/560x315/3606763.jpg',
        link: '2'
    },
    {
        name: 'Taco Seasoning I',
        url: 'http://images.media-allrecipes.com/userphotos/720x405/4090979.jpg',
        link: '2'
    },
];

var InfiniteList = React.createClass({
    getInitialState: function () {
        return {
            // dishes: [],
            elements: [], //this.buildElements(0, 20),
            isInfiniteLoading: false
        }
    },

    componentDidMount: function () {
        // $.get('/cookyourself/loaddata', function (result) {
        //     if (this.isMounted()) {
        //         // for (var i = 0; i < result.length; i++) {
        //         //     dishes.push(result[i])
        //         // }
        //         this.setState({
        //             dishes: result.data.dishes
        //         })
        //     }
        // }.bind(this));
        this.setState({
            elements : this.buildElements(0, 20),
        })
    },

    buildElements: function (start, end) {
        var elements = [];
        for (var i = start; i < end; i++) {
            // elements.push(<ListItem key={i} name={dishes[0].name} url={dishes[0].url} link={dishes[0].link}/>)
            // elements.push(<ListItem key={i+1} name={dishes[1].name} url={dishes[1].url} link={dishes[1].link}/>)
            elements.push(<ListItem key={i}
                                    name1={dishes[0].name} url1={dishes[0].url} link1={dishes[0].link}
                                    name2={dishes[1].name} url2={dishes[1].url} link2={dishes[1].link}
                                    name3={dishes[2].name} url3={dishes[2].url} link3={dishes[2].link}/>)
        }
        return elements;
    },

    handleInfiniteLoad: function () {
        var that = this;
        this.setState({
            isInfiniteLoading: true
        });
        setTimeout(function () {
            var elemLength = that.state.elements.length,
                newElements = that.buildElements(elemLength, elemLength + 30);
            that.setState({
                isInfiniteLoading: false,
                elements: that.state.elements.concat(newElements)
            });
        }, 2500);
    },

    elementInfiniteLoad: function () {
        return <div className="infinite-list-item">
            <h3 className="text-center" color="orange">Loading...</h3>
        </div>;
    },

    render: function () {
        return <Infinite useWindowAsScrollContainer
                         containerHeight={40}
                         elementHeight={250}
                         infiniteLoadBeginEdgeOffset={200}
                         onInfiniteLoad={this.handleInfiniteLoad}
                         loadingSpinnerDelegate={this.elementInfiniteLoad()}
                         isInfiniteLoading={this.state.isInfiniteLoading}>
            {this.state.elements}
        </Infinite>;
    }
});

// ReactDOM.render(<InfiniteList/>, document.getElementById('container'));