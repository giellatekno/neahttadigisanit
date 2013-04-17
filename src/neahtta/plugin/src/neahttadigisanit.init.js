// NDS_API_HOST references variable declared above in the bookmarklet
// compilation, to be referenced within bookmarklet js stored in user's
// browser (separate js from the actual bookmarklet.init.js, which is
// the whole app..
jQuery(document).ready(function (){
	// For some reason rangy needs to be initialized, but apparently only for
	// the bookmarklet.
    rangy.init();
    jQuery(document).selectToLookup({
        api_host: NDS_API_HOST + '/',
        tooltip: true,
        displayOptions: true,
        spinnerImg: NDS_API_HOST + '/static/img/spinner.gif'
    });
});
