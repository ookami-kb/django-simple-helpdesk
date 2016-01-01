angular.module('HelpdeskApp', ['ngMaterial', 'ngResource', 'md.data.table'])
    .factory('TicketList', ['$resource', function ($resource) {
        return $resource('/helpdesk/api/tickets/', {}, {
            query: {
                method: 'GET',
                isArray: true
            }
        })
    }])
    .controller('TicketListController', ['$scope', 'TicketList', function ($scope, TicketList) {
        $scope.tickets = TicketList.query();

        $scope.stateLabelClass = function (ticket) {
            var classes = ['state'];
            classes.push('state--' + ticket.state.machine_name);

            return classes.join(' ');
        };

        $scope.ticketRowClass = function (ticket) {
            var classes = [];
            if (ticket.state.resolved) {
                classes.push('row--resolved');
            }

            return classes.join(' ');
        };

        $scope.getIcon = function (priority) {
            return ['info', '', 'error'][priority];
        };

        $scope.openTicket = function (id) {
            window.location = '' + id + '/';
        };
    }])
;