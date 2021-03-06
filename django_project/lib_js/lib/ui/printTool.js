'use strict';

// global events
var EVENTS = require('../events');

var UI_Button = require('./button');

var PrintTool = function(options) {
    this.options = {
        // initial module options
    };

    // override and extend default options
    for (var opt in options) {
        if (options.hasOwnProperty(opt)) {
            this.options[opt] = options[opt];
        }
    }

    this.init();

    return {
        controller: this.controller,
        view: this.view
    };
};

PrintTool.prototype = {

    init: function() {
        var button = new UI_Button({
            style: 'i.fa.fa-print',
            title: 'Print'
        });

        this.controller = button.controller;
        this.view = button.view;

        button.controller.vm.events.on('button.activated', function () {
            EVENTS.emit('print.activate');
        });
        button.controller.vm.events.on('button.deactivated', function () {
            EVENTS.emit('print.deactivate');
        });

        // deactivate button if printControl was deactivated
        EVENTS.on('print.deactivate', function () {
            button.controller.vm.deactivate(true);
        });
    }
};

module.exports = PrintTool;
