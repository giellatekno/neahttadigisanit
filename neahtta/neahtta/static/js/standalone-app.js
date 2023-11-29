
function standaloneInit() {
    // Redirect links to not open up in the browser
    // https://gist.github.com/irae/1042167
    (function(document,navigator,standalone) {
        // prevents links from apps from oppening in mobile safari
        // this javascript must be the first script in your <head>
        if ((standalone in navigator) && navigator[standalone]) {
            var curnode, location=document.location, stop=/^(a|html)$/i;
            document.addEventListener('click', function(e) {
                curnode=e.target;
                while (!(stop).test(curnode.nodeName)) {
                    curnode=curnode.parentNode;
                }
                // Condidions to do this only on links to your own app
                // if you want all links, use if('href' in curnode) instead.
                if(
                    'href' in curnode && // is a link
                    (chref=curnode.href).replace(location.href,'').indexOf('#') && // is not an anchor
                    (   !(/^[a-z\+\.\-]+:/i).test(chref) ||                       // either does not have a proper scheme (relative links)
                        chref.indexOf(location.protocol+'//'+location.host)===0 ) // or is in the same protocol and domain
                ) {
                    // Some links are not actually links.
                    if(curnode.href !== "") {
                        e.preventDefault();
                        location.href = curnode.href;
                    } else {
                        return true;
                    }
                }
            },false);
        }
    })(document,window.navigator,'standalone');
}

// Detect the standalone browser
standaloneInit();
