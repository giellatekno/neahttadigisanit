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
        restrict: 'A',
        controller: function ($scope, $http, $element, $attrs) {
            var lem = $attrs.lemma;

            var paradigm_url = "/paradigm/" + $attrs.sourceLang + '/' + $attrs.targetLang + '/' + lem;

            var get_attrs = {};

            if ($attrs.posRestrict) {
                get_attrs['pos'] = $attrs.posRestrict;
            }

            $scope.requesting = false;
            // Wait a little bit to display that the request is in
            // progress, prevent blinking.

            // Wait until a little bit after load to begin requesting
            setTimeout(function(){
                $element.addClass('loading');
                $http({url: paradigm_url, method: "GET", params: get_attrs}).success(function(data){ 
                    $scope.paradigm = data.paradigms[0];
                    $element.removeClass('loading');
                    $element.find('.loading_spinner').remove();
                });
            }, 100);

        } ,
    }
});
