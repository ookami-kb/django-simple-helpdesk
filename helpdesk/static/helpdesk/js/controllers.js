var helpdeskControllers = angular.module('helpdeskControllers', []);

helpdeskControllers.controller('TicketListController', ['$scope', 'Ticket', function ($scope, Ticket) {

    function updateTicketList() {
        var response = Ticket.query({
            order_by: $scope.orderProp
        }, function () {
            $scope.tickets = response.objects;
        });
    }

    $scope.$watch('orderProp', updateTicketList);
    $scope.orderProp = '-priority';
}]);