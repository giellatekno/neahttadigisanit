/* jshint strict: false */
/* jshint camelcase: false */

var Tagsets;

__indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

Tagsets = (function() {
  function Tagsets(sets) {
    this.sets = sets;
  }

  Tagsets.prototype.add_tags = function(ts) {
      this.sets = ts;
      return true;
  };

  Tagsets.prototype.tag_has_set = function(t, s) {
    return _.intersection(this.sets[s], t).length > 0;
  };

  Tagsets.prototype.get_tagset_value = function(t, s) {
    return _.intersection(this.sets[s], t)[0];

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

window.tagsets = new Tagsets({});

var NDS = angular.module('NDS', [])
    .config(function($interpolateProvider, $httpProvider) {
        // set template expression symbols
        $interpolateProvider.startSymbol('<%');
        $interpolateProvider.endSymbol('%>');
        $httpProvider.defaults.withCredentials = true;
    });

NDS.filter('by_tagset', function(){
    return function(list, tagset){

        console.log("by_tagset");
        console.log(tagset);

        tag_filter = function(form) {
            console.log(form);
            return window.tagsets.tag_has_set(form.tag, tagset);
        }

        return _.filter(list, tag_filter);
    };
});

NDS.filter('get_tagset_value', function(){
    return function(tag, tagset){
        return window.tagsets.get_tagset_value(tag, tagset);
    };
});


NDS.filter('by_tagset_value', function(){
    return function(list, tagset, tagset_value){

        console.log("by_tagset_value");
        console.log(tagset);
        console.log(tagset_value);

        tag_filter = function(form) {
            console.log(form);
            return window.tagsets.tag_has_set_value(form.tag, tagset, tagset_value);
        }

        return _.filter(list, tag_filter);
    };
});


NDS.directive('wordParadigm', function() {
    return {
        restrict: 'A', // Attribute name word-paradigm
        scope: true,
        controller: function ($scope, $http, $element, $attrs) {
            var lem = $attrs.lemma;
            $scope._ = _;

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

                    window.tagsets = false;
                    $scope.tagsets = false;

                    // http_options
                    $http({url: paradigm_url, method: "OPTIONS", params: get_attrs})
                        .success(function(data){

                            window.tagsets = new Tagsets(data.tagsets);
                            $scope.tagsets = window.tagsets ;

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

                                            var o_keys = [
                                                'input',
                                                'user_friendly_tag',
                                                'generated_forms',
                                                'tag',
                                            ];

                                            var to_obj = function(p){return _.object(o_keys, p)};

                                            $scope.paradigm = _.map(data.paradigms[0],
                                                                    to_obj)

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

                        }); // http_options
                        

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
