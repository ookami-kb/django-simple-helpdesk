var helpdeskComponents = angular.module('helpdeskComponents', []);

helpdeskComponents.directive('issueCard', function() {
    return {
        restrict: 'E',
        transclude: true,
        scope: {},
        template: '<div class="mdl-card card-issue mdl-shadow--2dp"><div class="card-issue__content" ng-transclude></div></div>',
        replace: true
    }
});