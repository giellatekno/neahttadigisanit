jQuery(document).ready(function (){
	// For some reason rangy needs to be initialized, but apparently only for
	// the bookmarklet.
    jQuery(document).selectToLookup({
        api_host: NDS_API_HOST + '/',
    });
});
