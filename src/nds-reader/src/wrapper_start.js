// Global NDS space
//
// This goes along with wrapper_end.js to set up one big namespace for NDS. 

(function (){
    'use strict';

    (function(){
        // Undefine amd, requirejs, etc., because it conflicts with the local commonjs-require.

        var globals = typeof window !== 'undefined' ? window : global;

        globals.define = undefined;
        globals.require = undefined;
        globals.requirejs = undefined;

    }).call(this);

