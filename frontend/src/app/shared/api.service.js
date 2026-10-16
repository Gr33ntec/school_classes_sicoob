(function () {
  'use strict';

  // Fabrica de clientes REST: Api('students').list(params) etc.
  angular.module('schoolApp').factory('Api', function ($http, API_BASE_URL) {
    return function (resource) {
      var url = API_BASE_URL + '/' + resource;
      return {
        list: function (params) {
          return $http.get(url, { params: params }).then(function (r) {
            var d = r.data;
            return Array.isArray(d) ? { items: d, total: d.length } : d;
          });
        },
        create: function (body) { return $http.post(url, body).then(function (r) { return r.data; }); },
        update: function (id, body) { return $http.put(url + '/' + id, body).then(function (r) { return r.data; }); },
        remove: function (id) { return $http.delete(url + '/' + id); }
      };
    };
  });

  // Converte erros HTTP em mensagens de dominio, sem expor detalhes internos.
  angular.module('schoolApp').factory('ErrorMessage', function () {
    return function (err) {
      if (!err || err.status === -1) { return 'Nao foi possivel conectar ao servidor.'; }
      if (err.status === 404) { return 'Registro nao encontrado.'; }
      if (err.status === 409) {
        return (err.data && typeof err.data.detail === 'string' && err.data.detail) ||
          'Conflito: registro duplicado, turma lotada ou possui vinculos.';
      }
      if (err.status === 422 || err.status === 400) { return 'Dados invalidos. Revise o formulario.'; }
      return 'Erro inesperado. Tente novamente.';
    };
  });
})();
