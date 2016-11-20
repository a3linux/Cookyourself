/**
 * Created by yunpengx on 11/12/16.
 */
var React = require('react');
var ReactDOM = require('react-dom');
var dishesCookie = "dishes";

function createCookie(name,value,days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

function eraseCookie(name) {
	createCookie(name,"",-1);
}

function deleteAllCookies() {
    var cookies = document.cookie.split(";");

    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i];
        var eqPos = cookie.indexOf("=");
        var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:01 GMT;";
    }
}

var Dish = React.createClass({
    render: function () {
        var str = "myCanvas" + this.props.id;
        return (
            <div className="col-xs-12 col-md-4 col-lg-4">
                <a href={'/cookyourself/dish/' + this.props.id}>
                    <canvas id={str} className="img-thumbnail main_pic" width="533" height="300"/>
                </a>
                <h5 className="max-lines text-center">{this.props.name}</h5>
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
            var dw = 533;           //the width we desire
            var dh = 300;           //the height we desire
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
            all: [],            //used to store all the dishes
            dishes: [],         //used to store dishes
            alreadyLogin: 0,    //already login to the page
            loading: 0          //the status of loading: 0 - not loading, 1 - loading, 2 - nothing to load
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
        // console.log("before:" + document.cookie);
        var self = this;
        var alreadyLogin = this.state.alreadyLogin; //already Login status
        var oldCookie = "";
        var url = '/cookyourself/loadmore';
        // console.log("alreadyLogin:" + alreadyLogin);
        if (window.performance) {
            var type = performance.navigation.type;
            // console.log("type:" + type);
            if (alreadyLogin == 0 && (type == 0 || type == 1 || type == 2)) { //0 - TYPE_NAVIGATE, 1 - TYPE_RELOAD, 2 - TYPE_BACK_FORWARD
                // console.log('refresh cookies');
                eraseCookie(dishesCookie);
                oldCookie = readCookie(dishesCookie);
            } else {
                // console.log('no need to refresh cookies');
                oldCookie = readCookie(dishesCookie);
            }
        }
        // console.log("after:" + document.cookie);
        // console.log("oldCookie:" + oldCookie);

        // Empty the current array. This will trigger a render
        this.setState({dishes: [], loading: 1});
        var newCookie = [];
        $.get(url).done(function (data) {
            if (!data || !data.sets || !data.sets.length) {
                // console.log("no more dishes");
                self.setState({loading: 2});
                return;
            }

            var dishes = data.sets.map(function (p) {
                if (p.id != '') {
                    newCookie.push(p.id);
                }
                return {
                    id: p.id,
                    name: p.name,
                    url: p.url,
                };
            });

            // console.log("newCookie:" + newCookie.toString());
            if (oldCookie == null) {
                oldCookie = ""
            }
            var allCookies = oldCookie.concat(newCookie);
            createCookie(dishesCookie, allCookies, 0);
            // console.log("allCookies:" + allCookies);

            // update the component's state. This will trigger a render
            self.setState({all: self.state.all.concat(dishes), loading: 0, alreadyLogin: 1});
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