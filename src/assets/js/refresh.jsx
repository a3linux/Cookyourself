/**
 * Created by yunpengx on 11/12/16.
 */
var React = require('react');
var ReactDOM = require('react-dom');

var PictureList = React.createClass({
    getInitialState: function () {
        // console.info("enter getInitialState")
        // the pictures array will be populated via AJAX.
        return {
            pictures: [],
            loading: false
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
        // this.refresh();
    },

    refresh: function () {
        var self = this;
        var url = '/cookyourself/loaddata'; // specify the url to get images that we need to render

        // Empty the current array. This will trigger a render
        this.setState({pictures: [], loading: true});

        $.getJSON(url, function (result) {
            if (!result || !result.data || !result.data.length) {
                console.log("no more pictures");
                return;
            }

            var pictures = result.data.map(function (p) {
                return {
                    id: p.id,
                    name: p.name,
                    url: p.url,
                };
            });

            //update the component's state. This will trigger a render
            self.setState({pictures: pictures, loading: false});
        });
    },

    render: function () {
        var refreshButton;

        // Make the refresh button spin and disabled it while loading.
        if (this.state.loading) {
            refreshButton = <div className="btn-warning" visibility="hidden"></div>
        } else {
            refreshButton = <div className="btn-warning" onClick={this.refresh}></div>
        }
        // Return the component content. Pictures can be rendered by looping through.
        return (
            <div className="PictureList">
                {
                    this.state.pictures.map(function (value) {
                        return <div className="col-xs-12 col-md-4 col-lg-4">
                            <a href={'/cookyourself/dish/' + value.id}>
                                <img className="img-thumbnail post_picture" width="100%" height="100%"
                                     src={value.url} alt="Dish"/></a>
                            <h5 className="text-center">{value.name}</h5>
                        </div>
                    })
                }
                {refreshButton}
            </div>
        )
    }
});

ReactDOM.render(<PictureList/>, document.getElementById('container'));