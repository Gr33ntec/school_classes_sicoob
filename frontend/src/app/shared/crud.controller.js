(function () {
  'use strict';

  // Base reutilizada pelos controllers de cada funcionalidade.
  // config: { title, resource, columns:[{key,label}], fields:[{key,label,type,required,options}], defaults }
  angular.module('schoolApp').factory('CrudBase', function (Api, ErrorMessage) {
    return function (vm, config) {
      var api = Api(config.resource);

      vm.title = config.title;
      vm.columns = config.columns;
      vm.fields = config.fields;
      vm.items = [];
      vm.total = 0;
      vm.page = 1;
      vm.pageSize = 10;
      vm.loading = false;
      vm.error = null;
      vm.editing = null;
      vm.form = null;

      function load() {
        vm.loading = true;
        vm.error = null;
        api.list({ page: vm.page, page_size: vm.pageSize })
          .then(function (data) { vm.items = data.items; vm.total = data.total; })
          .catch(function (e) { vm.error = ErrorMessage(e); })
          .finally(function () { vm.loading = false; });
      }

      vm.reload = load;
      vm.totalPages = function () { return Math.max(1, Math.ceil(vm.total / vm.pageSize)); };
      vm.goTo = function (p) {
        if (p < 1 || p > vm.totalPages()) { return; }
        vm.page = p;
        load();
      };

      vm.new = function () {
        vm.editing = null;
        vm.form = angular.copy(config.defaults || {});
      };
      vm.edit = function (item) {
        vm.editing = item.id;
        vm.form = angular.copy(item);
      };
      vm.cancel = function () { vm.form = null; vm.editing = null; };

      vm.save = function (formCtrl) {
        if (formCtrl.$invalid) { return; }
        var op = vm.editing ? api.update(vm.editing, vm.form) : api.create(vm.form);
        vm.error = null;
        op.then(function () { vm.cancel(); load(); })
          .catch(function (e) { vm.error = ErrorMessage(e); });
      };

      vm.remove = function (item) {
        if (!window.confirm('Confirmar exclusao deste registro?')) { return; }
        api.remove(item.id)
          .then(function () { load(); })
          .catch(function (e) { vm.error = ErrorMessage(e); });
      };

      // Carrega opcoes de campos select a partir de outro recurso.
      config.fields.forEach(function (f) {
        if (f.optionsResource) {
          Api(f.optionsResource).list({ page: 1, page_size: 100 }).then(function (d) {
            f.options = d.items.map(function (o) {
              return { value: o.id, label: o[f.optionsLabel || 'name'] };
            });
          });
        }
      });

      load();
    };
  });
})();
