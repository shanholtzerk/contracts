// additional methods for select2 Editor fieldType
// must be initialized after editor.select2.js

(function( factory ){
    if ( typeof define === 'function' && define.amd ) {
        // AMD
        define( ['jquery', 'datatables', 'datatables-editor'], factory );
    }
    else if ( typeof exports === 'object' ) {
        // Node / CommonJS
        module.exports = function ($, dt) {
            if ( ! $ ) { $ = require('jquery'); }
            factory( $, dt || $.fn.dataTable || require('datatables') );
        };
    }
    else if ( jQuery ) {
        // Browser standard
        factory( jQuery, jQuery.fn.dataTable );
    }
}(function( $, DataTable ) {
'use strict';


if ( ! DataTable.ext.editorFields ) {
    DataTable.ext.editorFields = {};
}
 
var _fieldTypes = DataTable.Editor ?
    DataTable.Editor.fieldTypes :
    DataTable.ext.editorFields;

_fieldTypes.select2.AddOption = function(conf, opts) {
    var elOpts = conf._input[0].options;

    if ( opts ) {
        DataTable.Editor.pairs( opts, conf.optionsPair, function ( val, label, i ) {
            var thisoption = new Option( label, val );
            elOpts[ elOpts.length ] = thisoption ;
            // _fieldTypes.select2.inst ( 'append', thisoption );
        } );
        
        // don't fire change because if in process of updating option causes form to remain displayed
        // conf._input.trigger( 'change', {editor: true} );
    }
};

}));
