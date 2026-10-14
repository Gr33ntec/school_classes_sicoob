(function () {
  'use strict';

  angular.module('schoolApp').controller('TeachersController', function (CrudBase) {
    CrudBase(this, {
      title: 'Professores',
      resource: 'teachers',
      columns: [
        { key: 'employee_code', label: 'Codigo' },
        { key: 'full_name', label: 'Nome' },
        { key: 'email', label: 'E-mail' },
        { key: 'status', label: 'Status' }
      ],
      fields: [
        { key: 'employee_code', label: 'Codigo do funcionario', required: true },
        { key: 'full_name', label: 'Nome completo', required: true },
        { key: 'email', label: 'E-mail', type: 'email' },
        { key: 'phone', label: 'Telefone' },
        { key: 'status', label: 'Status', type: 'select', required: true,
          options: [{ value: 'active', label: 'Ativo' }, { value: 'inactive', label: 'Inativo' }] }
      ],
      defaults: { status: 'active' }
    });
  });
})();
