'use strict';

var m = require('mithril');


var VIEW = function (ctrl) {
    // do not add anything else to the VIEW, it should never initialize anything
    return render(ctrl);
};

var render = function(ctrl) {
    return m('div.sl-toolbox', [
        ctrl.vm.components.map(function(component) {
            return component.view(component.controller);
        })
    ]);
};

module.exports = VIEW;
