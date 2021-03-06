'use strict';

var _ = require('lodash');
var m = require('mithril');

var Jvent = require('jvent');

var Feature = function(data) {
    this.id = m.prop(data.id);
    this.toggled = m.prop(true);

    this.properties = {};
};

Feature.prototype = {
    toggle: function() {
        if (this.toggled()) {
            this.toggled(false);
        } else {
            this.toggled(true);
        }
    },

    setProperties: function(properties) {
        var self = this;
        _.forEach(properties, function(value, attribute) {
            if (properties.hasOwnProperty(attribute)) {
                self.properties[attribute] = m.prop(value);
            }
        });
    }
};

var FeatureList = Array;

var VIEWMODEL = function(options) {
    this.init(options);
};

VIEWMODEL.prototype = {
    init: function(options) {
        // initialize component events
        this.events = new Jvent();

        this.options = options;
        this.list = new FeatureList();
    },
    set: function(data) {
        var self = this;
        this.list = new FeatureList();

        _.each(data, function(feature) {
            var geometryName = feature.getGeometryName();
            var properties = feature.getProperties();

            var newFeature = new Feature({
                id: feature.getId()
            });
            // omit geometry from properties (OL3 api) as it's included
            newFeature.setProperties(_.omit(properties, geometryName));
            self.list.push(newFeature);
        });

        // if there are some results
        if (this.list.length > 0) {
            this.events.emit('results.show');
        } else {
            this.events.emit('results.hide');
        }
    },

    ev_resultClicked: function(item) {
        this.vm.events.emit('result.click', {
            result: item
        });
    },

    ev_toggleItem: function (item) {
        item.toggle();
    }
};

module.exports = VIEWMODEL;
