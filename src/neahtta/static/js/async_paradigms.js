/* jshint strict: false */
/* jshint camelcase: false */

var Tagsets;

__indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

Tagsets = (function() {
  function Tagsets(sets) {
    this.sets = sets;
  }

  Tagsets.prototype.tag_has_set = function(t, s) {
    return _.intersection(this.sets[s], t).length > 0;
  };

  Tagsets.prototype.tag_has_set_value = function(t, s, v) {
    in_set = _.intersection(this.sets[s], t);
    return __indexOf.call(in_set, v) >= 0
  };

  Tagsets.prototype.filter_tags_by_set = function(ts, s) {
    var _filter_pred = (function(_this, _s) {
        return function(t) {
            return _this.tag_has_set(t, _s);
        };
    })(this, s);

    return _.filter(ts, _filter_pred);
  };

  Tagsets.prototype.filter_tags_by_set_value = function(ts, s, v) {
    var _filter_pred = (function(_this, _s, _v) {
        return function(t) {
            return _this.tag_has_set_value(t, _s, _v);
        };
    })(this, s, v);

    return _.filter(ts, _filter_pred);
  };


  return Tagsets;

})();

window.tagsets = new Tagsets([]);

var NDS = angular.module('NDS', [])
    .config(function($interpolateProvider, $httpProvider) {
        // set template expression symbols
        $interpolateProvider.startSymbol('<%');
        $interpolateProvider.endSymbol('%>');
        $httpProvider.defaults.withCredentials = true;
    });

// NDS.filter('by_tagset', function(){
//     // TODO:
//     return function(list, tagset){
//         console.log("omg");
//         console.log(list);
//         console.log(tagset);
//         return list;
//     };
// });


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
            $scope.tagsets = false;

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
                                    $scope.tagsets = new Tagsets(data.tagsets);
                                    window.tagsets = new Tagsets($scope.tagsets);

                                    $scope.paradigm = data.paradigms[0];
                                    $scope.no_paradigm = false;
                                } else {
                                    $scope.paradigm = false;
                                    $scope.tagsets = false;
                                    $scope.no_paradigm = true;
                                }
                            } else {
                                $scope.paradigm = false;
                                $scope.tagsets = false;
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
