(function () {
  'use strict';

  angular.module('schoolApp').controller('CoursesController', function (CrudBase) {
    CrudBase(this, {
      title: 'Cursos',
      resource: 'courses',
      columns: [
        { key: 'course_code', label: 'Codigo' },
        { key: 'name', label: 'Nome' },
        { key: 'workload_hours', label: 'Carga horaria' },
        { key: 'status', label: 'Status' }
      ],
      fields: [
        { key: 'course_code', label: 'Codigo do curso', required: true },
        { key: 'name', label: 'Nome', required: true },
        { key: 'description', label: 'Descricao' },
        { key: 'workload_hours', label: 'Carga horaria (h)', type: 'number', required: true, min: 1 },
        { key: 'status', label: 'Status', type: 'select', required: true,
          options: [{ value: 'active', label: 'Ativo' }, { value: 'inactive', label: 'Inativo' }] }
      ],
      defaults: { status: 'active' }
    });
  });
})();
