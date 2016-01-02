angular.module('HelpdeskApp', ['ngMaterial', 'ngResource', 'md.data.table', 'ngSanitize'])
    .factory('TicketList', ['$resource', function ($resource) {
        return $resource('/helpdesk/api/tickets/:id.json', {}, {
            query: {
                method: 'GET',
                isArray: false
            }
        })
    }])
    .factory('StateList', ['$resource', function ($resource) {
        return $resource('/helpdesk/api/states/', {}, {})
    }])
    .factory('AssigneeList', ['$resource', function ($resource) {
        return $resource('/helpdesk/api/assignees/', {}, {})
    }])
    .controller('TicketController', ['$scope', 'TicketList', function ($scope, TicketList) {
        $scope.ticket = TicketList.query({id: ticketId})
    }])
    .controller('TicketListController', ['$scope', 'TicketList', 'StateList', 'AssigneeList',
        function ($scope, TicketList, StateList, AssigneeList) {
            $scope.updateTicketList = function (page, limit) {
                page = typeof page !== 'undefined' ? page : 1;
                limit = typeof limit !== 'undefined' ? limit : 15;

                $scope.tickets = TicketList.query({
                    state: $scope.currentState,
                    assignee: $scope.currentAssignee,
                    search: $scope.currentSearch,
                    page: page,
                    limit: limit
                });
            };

            $scope.states = StateList.query();
            $scope.currentState = "";

            $scope.assignees = AssigneeList.query();
            $scope.currentAssignee = "me";

            $scope.currentSearch = '';

            $scope.updateTicketList();

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