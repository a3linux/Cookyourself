/**
 * Created by yunpengx on 11/12/16.
 */
var React = require('react');
var ReactDOM = require('react-dom');

function Dish(props) {
    return (
        <div className="col-xs-12 col-md-4 col-lg-4">
            <a href={'/cookyourself/dish/' + props.id}>
                <img className="img-thumbnail main_pic" width="100%" height="100%"
                     src={props.url} alt="Dish"/></a>
            <h5 className="text-center">{props.name}</h5>
        </div>
    );
}

var DishList = React.createClass({
    getInitialState: function () {
        // console.info("enter getInitialState")
        // the dishes array will be populated via AJAX.
        return {
            all: [],        //used to store all the dishes
            dishes: [],     //used to store dishes
            maxID: 0,       //maxID for dishes
            loading: false  //the status of loading
        };
    },

    componentDidMount: function () {
        // console.info("enter componentDidMount")
        // when the components loads, refresh the images.
        this.refresh();
    },

    componentDidUpdate: function () {
        // We need to tell the carousel to refresh when the content changes.
        // This is to ensure that it's displayed correctly.
        this.imageResize();
    },

    imageResize: function () {
        $('.main_pic').each(function () {
            var standardHeight = 200;       // standard height for post images
            var ratio = 0;                  // used for aspect ratio
            var width = $(this).width();    // current image width
            var height = $(this).height();  // current image height

            // check if the current height is larger than the max
            if (height != standardHeight) {
                ratio = standardHeight / height;
                $(this).css("height", standardHeight);
                $(this).css("width", ratio * width);
                width = width * ratio;
            }
        })
    },

    refresh: function () {
        var self = this;
        var currMaxID = this.state.maxID; //the current maxID
        var url = '/cookyourself/loadmore/' + currMaxID; // specify the url to get images that we need to render
        // console.log(currMaxID);

        // Empty the current array. This will trigger a render
        this.setState({dishes: [], loading: true});

        $.get(url).done(function (data) {
            if (!data || !data.sets || !data.sets.length) {
                console.log("no more dishes");
                return;
            }

            var dishes = data.sets.map(function (p) {
                console.log(p.url)
                return {
                    id: p.id,
                    name: p.name,
                    url: p.url,
                };
            });

            var newMaxID = currMaxID + data.sets.length; //FIXME
            // console.log(newMaxID)
            //update the component's state. This will trigger a render
            self.setState({all: self.state.all.concat(dishes), loading: false, maxID: newMaxID});
        });
    },

    render: function () {
        var refreshButton;

        // Make the refresh button spin and disabled it while loading.
        if (this.state.loading) {
            refreshButton = <div className="col-xs-12 col-md-12 col-lg-12">
                <a className="btn-refresh outline" visibility="hidden"></a>
            </div>
        } else {
            refreshButton = <div className="col-xs-12 col-md-12 col-lg-12 div-refresh">
                <a className="btn-refresh outline" onClick={this.refresh}>Load more...</a>
            </div>
        }
        // Return the component content. dishes can be rendered by looping through.
        return (
            <div>
                <div className="DishList">
                    {
                        this.state.all.map(function (value) {
                            return (<Dish id={value.id} name={value.name} url={value.url}/>)
                        })
                    }
                </div>
                <br/>
                {refreshButton}
            </div>
        )
    }
});

ReactDOM.render(<DishList/>, document.getElementById('content'));