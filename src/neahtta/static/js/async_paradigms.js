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

            // Wait until a little bit after load to begin requesting
            $element.addClass('loading');
            $scope.complete = false;
            $scope.paradigm = false;
            setTimeout(function(){
                $element.addClass('loading');
                $http({url: paradigm_url, method: "GET", params: get_attrs})
                    .success(function(data){ 
                        $element.removeClass('loading');
                        $element.find('.loading_spinner').remove();

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

        } ,
    }
});
