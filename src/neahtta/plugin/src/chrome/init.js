jQuery(self).ready(function (){
    // Register the input form with options
    // NOTE: this doesn't need to be included for mouseclick lookups
    jQuery(document).find('#neahttadigisanit').digiSanit();

    // Enable options for inline clicking
    // jQuery(document).selectToLookup({
    //   tooltip: true,
    //   displayOptions: true
    // });
});

