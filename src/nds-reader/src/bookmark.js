(function () {
    var NDS_API_HOST             = 'OMGNDS_API_HOSTBBQ' 
      , NDS_MEDIA_HOST           = 'OMGNDS_MEDIA_HOSTBBQ'
      , NDS_BOOKMARK_VERSION     = '0.0.4'
      ;

    var PFX = (window.location.protocol === 'file:' ? 'http:' : '') ;

    var nds_css      = document.createElement('link') ;
        nds_css.href = PFX + NDS_MEDIA_HOST + '/static/css/jquery.neahttadigisanit.css' ;
        nds_css.rel  = 'stylesheet' ;

    var nds_book      = document.createElement('script') ;
        nds_book.type = 'text/javascript' ;
        nds_book.src  = PFX + NDS_MEDIA_HOST + '/static/js/bookmarklet.min.js' ;
       
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
