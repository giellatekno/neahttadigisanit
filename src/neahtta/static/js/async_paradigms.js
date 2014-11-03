/* jshint strict: false */
/* jshint camelcase: false */

var NDS = angular.module('NDS', []).
    config(function($interpolateProvider, $httpProvider) {
        // set template expression symbols
        $interpolateProvider.startSymbol('<%');
        $interpolateProvider.endSymbol('%>');
        $httpProvider.defaults.withCredentials = true;
    });


NDS.directive('wordParadigm', function() {
    return {
        restrict: 'A', // Attribute name word-paradigm
        scope: true,
        controller: function ($scope, $http, $element, $attrs) {
            var lem = $attrs.lemma;

            var paradigm_url = "/paradigm/" + $attrs.sourceLang + '/' + $attrs.targetLang + '/' + lem;

            var get_attrs = {};

            if ($attrs.posRestrict) {
                get_attrs['pos'] = $attrs.posRestrict;
            }

            // Wait until a little bit after load to begin requesting
            $element.addClass('loading');
            $scope.complete = false;
            $scope.paradigm = false;

            // define this as a function because we'll use it as an
            // event too

            function run_request () {
                setTimeout(function(){
                    $element.addClass('loading');
                    $http({url: paradigm_url, method: "GET", params: get_attrs})
                        .success(function(data){ 
                            $element.removeClass('loading');
                            $element.find('.loading_spinner').hide();

                            window.thanks_android = setInterval( function (){
                                if ($scope.paradigm) {
                                    $element.removeClass('loading');
                                    $element.find('.loading_spinner').hide();
                                    clearInterval(window.thanks_android);
                                    delete window.thanks_android;
                                }
                            }, 100);

                            $scope.complete = true;

                            if(data.paradigms.length > 0) {
                                if(data.paradigms[0].length > 0) {
                                    $scope.paradigm = data.paradigms[0];
                                    $scope.no_paradigm = false;
                                } else {
                                    $scope.paradigm = false;
                                    $scope.no_paradigm = true;
                                }
                            } else {
                                $scope.paradigm = false;
                                $scope.no_paradigm = true;
                            }
                        })
                }, 100);
            }


            if($element.is(":visible")) {
                run_request();
            } else {
                // If this needs to be responsive, this works, but be
                // careful... 
                //
                // var visibility_check = setInterval(function(){
                //     // Watch for the element to become visible
                //     if ($element.is(":visible")) {
                //         clearInterval(visibility_check);
                //         run_request();
                //     }
                // }, 3000);
            }

        } ,
    }
});
