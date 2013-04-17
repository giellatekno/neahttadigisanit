jQuery(document).ready(function (){
    // Register the input form with options
    // NOTE: this doesn't need to be included for mouseclick lookups
    // jQuery('#neahttadigisanit').digiSanit();

    // Grab from WP's localize object
    spinner_path = plugin_paths.spinner ;

    // Enable options for inline clicking
    jQuery(document).selectToLookup({
      tooltip: true,
      displayOptions: true,
      spinnerImg: spinner_path
    });
});
