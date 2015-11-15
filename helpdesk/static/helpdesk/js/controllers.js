var helpdeskControllers = angular.module('helpdeskControllers', []);

helpdeskControllers.controller('TicketListController', ['$scope', 'Ticket', 'State', function ($scope, Ticket, State) {

    function updateTicketList() {
        var params = {
            order_by: $scope.orderProp
        };
        if ($scope.stateFilter) {
            params['state'] = $scope.stateFilter;
        }
        var response = Ticket.query(params, function () {
            $scope.tickets = response.objects;
        });
    }

    function updateStateList() {
        var response = State.query(function () {
            $scope.states = response.objects;
            $scope.states.unshift({
                machine_name: null,
                title: 'any'
            });
        });
    }

    $scope.customerLabel = function (ticket) {
        if (ticket.customer) {
            return '<strong>' + ticket.customer + '</strong>';
        }

        return '';
    };

    $scope.$watch('orderProp', updateTicketList);
    $scope.orderProp = '-priority';

    $scope.assignee = 'me';
    $scope.state = 'any';

    updateStateList();
    $scope.stateFilter = null;

    $scope.$watch('stateFilter', updateTicketList);
}]);