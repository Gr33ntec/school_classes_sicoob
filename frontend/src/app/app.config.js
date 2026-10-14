(function () {
  'use strict';

  angular.module('schoolApp')
    .constant('API_BASE_URL', 'http://localhost:8000/api/v1')
    .config(function ($routeProvider, $locationProvider) {
      $locationProvider.hashPrefix('!');

      ['students', 'teachers', 'courses', 'classes', 'enrollments'].forEach(function (name) {
        var ctrl = name.charAt(0).toUpperCase() + name.slice(1) + 'Controller';
        $routeProvider.when('/' + name, {
          templateUrl: 'app/shared/crud.html',
          controller: ctrl,
          controllerAs: 'vm'
        });
      });

      $routeProvider.otherwise({ redirectTo: '/students' });
    });
})();
