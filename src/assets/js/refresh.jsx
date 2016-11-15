/**
 * Created by yunpengx on 11/12/16.
 */
var React = require('react');
var ReactDOM = require('react-dom');

var Dish = React.createClass({
    getInitialState: function () {
        return {
            canvasId: '',
        }
    },

    render: function () {
        var str = "myCanvas" + this.props.id;
        return (
            <div className="col-xs-12 col-md-4 col-lg-4">
                <a href={'/cookyourself/dish/' + this.props.id}>
                    <canvas id={str} className="img-thumbnail main_pic" width="533" height="300"/>
                </a>
                <h5 className="text-center">{this.props.name}</h5>
            </div>
        )
    },

    cropImage: function () {
        var canvasId = "myCanvas" + this.props.id;
        var canvas = document.getElementById(canvasId);
        var ctx = canvas.getContext("2d");
        var imgObj = new Image();

        imgObj.onload = function () {
            var sx = 0;
            var sy = 0;
            var sw = this.width;    //the url pic width
            var sh = this.height;   //the url pic height
            var dw = 533;
            var dh = 300;
            var dx = 0;
            var dy = 0;

            //console.log("w:" + sw + "h:" + sh);
            ctx.drawImage(imgObj, sx, sy, sw, sh, dx, dy, dw, dh);
        };
        imgObj.src = this.props.url;
    },

    componentDidMount: function () {
        // resize the image we have rendered
        this.cropImage();
    },
});

var DishList = React.createClass({
    getInitialState: function () {
        // the dishes array will be populated via AJAX.
        return {
            all: [],        //used to store all the dishes
            dishes: [],     //used to store dishes
            maxID: 0,       //maxID for dishes
            loading: 0      //the status of loading: 0 - not loading, 1 - loading, 2 - nothing to load
        };
    },

    componentDidMount: function () {
        // when the components loads, refresh the images.
        this.refresh();
    },

    componentDidUpdate: function () {
        // resize the image we have rendered
        //this.imageResize();
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
        this.setState({dishes: [], loading: 1});

        $.get(url).done(function (data) {
            if (!data || !data.sets || !data.sets.length) {
                console.log("no more dishes");
                self.setState({loading: 2});
                return;
            }

            var dishes = data.sets.map(function (p) {
                // console.log(p.url)
                return {
                    id: p.id,
                    name: p.name,
                    url: p.url,
                };
            });

            var newMaxID = currMaxID + data.sets.length; //FIXME
            // console.log(newMaxID)
            //update the component's state. This will trigger a render
            self.setState({all: self.state.all.concat(dishes), loading: 0, maxID: newMaxID});
        });
    },

    render: function () {
        var refreshButton;

        // Make the refresh button spin and disabled it while loading.
        if (this.state.loading == 0) {
            refreshButton = <div className="col-xs-12 col-md-12 col-lg-12 div-refresh">
                <a className="btn-refresh outline" onClick={this.refresh}>Load more...</a>
            </div>
        } else if (this.state.loading == 1) {
            refreshButton = <div className="col-xs-12 col-md-12 col-lg-12">
                <a className="btn-refresh outline" visibility="hidden"></a>
            </div>
        } else {
            refreshButton = <div className="col-xs-12 col-md-12 col-lg-12 div-refresh">
                <a className="btn-refresh outline" onClick={this.refresh}>Over all...</a>
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