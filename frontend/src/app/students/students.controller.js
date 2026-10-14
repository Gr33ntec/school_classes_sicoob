(function () {
  'use strict';

  angular.module('schoolApp').controller('StudentsController', function (CrudBase) {
    CrudBase(this, {
      title: 'Alunos',
      resource: 'students',
      columns: [
        { key: 'registration_code', label: 'Matricula' },
        { key: 'full_name', label: 'Nome' },
        { key: 'email', label: 'E-mail' },
        { key: 'status', label: 'Status' }
      ],
      fields: [
        { key: 'registration_code', label: 'Codigo de matricula', required: true },
        { key: 'full_name', label: 'Nome completo', required: true },
        { key: 'email', label: 'E-mail', type: 'email' },
        { key: 'phone', label: 'Telefone' },
        { key: 'birth_date', label: 'Nascimento', type: 'date' },
        { key: 'status', label: 'Status', type: 'select', required: true,
          options: [{ value: 'active', label: 'Ativo' }, { value: 'inactive', label: 'Inativo' }] }
      ],
      defaults: { status: 'active' }
    });
  });
})();
