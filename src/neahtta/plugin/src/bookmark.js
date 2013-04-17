(function () {
    var NDS_API_HOST             = 'http://sanit.oahpa.no' 
      , NDS_BOOKMARK_VERSION     = '0.0.3'
      ;

    var nds_css      = document.createElement('link') ;
        nds_css.href = NDS_API_HOST + '/static/css/jquery.neahttadigisanit.css' ;
        nds_css.rel  = 'stylesheet' ;

    var nds_book      = document.createElement('script') ;
        nds_book.type = 'text/javascript' ;
        nds_book.src  = NDS_API_HOST + '/static/js/bookmarklet.min.js' ;
       
    window.NDS_API_HOST = NDS_API_HOST ;
    window.NDS_BOOKMARK_VERSION = NDS_BOOKMARK_VERSION ;

    if (window.location.hostname == "skuvla.info" && window.frames.length > 0) {
        var d;
        d = window.frames[1];
        d.window.NDS_API_HOST = window.NDS_API_HOST
        d.document.getElementsByTagName('head')[0].appendChild(nds_css);
        d.document.getElementsByTagName('body')[0].appendChild(nds_book);
    } else {
        document.getElementsByTagName('head')[0].appendChild(nds_css) ;
        document.getElementsByTagName('body')[0].appendChild(nds_book) ;
    }
})();
