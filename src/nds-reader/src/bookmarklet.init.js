// API_HOST references variable declared above in the bookmarklet
// compilation.
jQuery(document).ready(function (){
    // For some reason rangy needs to be initialized here, but only for the
    // bookmarklet
    rangy = require('rangy');
    rangy.init();
    jQuery(document).selectToLookup({
        api_host: NDS_API_HOST + '/',
    });
});
