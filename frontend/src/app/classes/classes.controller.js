(function () {
  'use strict';

  angular.module('schoolApp').controller('ClassesController', function (CrudBase) {
    CrudBase(this, {
      title: 'Turmas',
      resource: 'classes',
      columns: [
        { key: 'class_code', label: 'Codigo' },
        { key: 'course_id', label: 'Curso (id)' },
        { key: 'teacher_id', label: 'Professor (id)' },
        { key: 'start_date', label: 'Inicio' },
        { key: 'end_date', label: 'Fim' },
        { key: 'max_students', label: 'Vagas' },
        { key: 'status', label: 'Status' }
      ],
      fields: [
        { key: 'class_code', label: 'Codigo da turma', required: true },
        { key: 'course_id', label: 'Curso', type: 'select', required: true,
          optionsResource: 'courses', optionsLabel: 'name' },
        { key: 'teacher_id', label: 'Professor', type: 'select', required: true,
          optionsResource: 'teachers', optionsLabel: 'full_name' },
        { key: 'start_date', label: 'Inicio', type: 'date', required: true },
        { key: 'end_date', label: 'Fim', type: 'date', required: true },
        { key: 'max_students', label: 'Vagas', type: 'number', required: true, min: 1 },
        { key: 'status', label: 'Status', type: 'select', required: true,
          options: [
            { value: 'planned', label: 'Planejada' }, { value: 'active', label: 'Ativa' },
            { value: 'completed', label: 'Concluida' }, { value: 'cancelled', label: 'Cancelada' }
          ] }
      ],
      defaults: { status: 'planned' }
    });
  });
})();
