(function () {
  'use strict';

  angular.module('schoolApp').controller('EnrollmentsController', function (CrudBase) {
    CrudBase(this, {
      title: 'Matriculas',
      resource: 'enrollments',
      columns: [
        { key: 'student_id', label: 'Aluno (id)' },
        { key: 'class_id', label: 'Turma (id)' },
        { key: 'status', label: 'Status' },
        { key: 'final_grade', label: 'Nota final' }
      ],
      fields: [
        { key: 'student_id', label: 'Aluno', type: 'select', required: true,
          optionsResource: 'students', optionsLabel: 'full_name' },
        { key: 'class_id', label: 'Turma', type: 'select', required: true,
          optionsResource: 'classes', optionsLabel: 'class_code' },
        { key: 'status', label: 'Status', type: 'select', required: true,
          options: [
            { value: 'enrolled', label: 'Matriculado' }, { value: 'completed', label: 'Concluido' },
            { value: 'cancelled', label: 'Cancelado' }
          ] },
        { key: 'final_grade', label: 'Nota final (0-100)', type: 'number', min: 0, max: 100 }
      ],
      defaults: { status: 'enrolled' }
    });
  });
})();
