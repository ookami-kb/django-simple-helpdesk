var helpdeskControllers = angular.module('helpdeskControllers', []);

helpdeskControllers.controller('TicketListController', ['$scope', 'Ticket', 'State', 'Project',
    function ($scope, Ticket, State, Project) {

        function updateTicketList() {
            var params = {
                order_by: $scope.orderProp
            };
            if ($scope.stateFilter) {
                params['st'] = $scope.stateFilter;
            }
            if ($scope.projectFilter) {
                params['prj'] = $scope.projectFilter;
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

        function updateProjectList() {
            var response = Project.query(function () {
                $scope.projects = response.objects;
                $scope.projects.unshift({
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

        updateProjectList();
        $scope.projectFilter = null;
        $scope.$watch('projectFilter', updateTicketList);
    }]);