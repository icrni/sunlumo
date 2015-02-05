'use strict';

var m = require('mithril');
var _ = require('lodash');


var VIEW = function (ctrl) {
    // do not add anything else to the VIEW, it should never initialize anything
    return render(ctrl);
};

var render = function(ctrl) {
    return  m('img.logo', {
        'src': '/static/img/spinner7.gif',
        'class': (ctrl.vm.active()) ? '' : 'hide'
    });
};


module.exports = VIEW;
