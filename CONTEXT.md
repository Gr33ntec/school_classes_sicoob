# CONTEXT.md

## Visao do projeto

Sistema web para gerenciamento academico de uma escola, com operacoes CRUD para alunos, professores, cursos e turmas, alem do gerenciamento das matriculas dos alunos nas turmas.

### Tecnologias

- Frontend: AngularJS 1.x, consumindo uma API HTTP/JSON.
- Backend: Python. Recomendacao: FastAPI, SQLAlchemy 2 e Alembic para migrations.
- Banco de dados: MySQL 8+, engine InnoDB e charset `utf8mb4`.

> AngularJS 1.x esta fora de suporte oficial. Como e um requisito deste projeto, mantenha a aplicacao organizada e planeje uma migracao para Angular atual se o produto continuar evoluindo.

## Modelo de dados

O modelo e relacional e normalizado. Uma turma pertence a um curso e tem um professor responsavel. Alunos e turmas se relacionam muitos-para-muitos por meio de matriculas. Se houver necessidade de varios professores na mesma turma, substitua `teacher_id` por uma tabela associativa `class_teachers`.

### Relacionamentos

- `courses` 1:N `school_classes`
- `teachers` 1:N `school_classes`
- `students` 1:N `enrollments`
- `school_classes` 1:N `enrollments`
- `students` N:N `school_classes`, resolvido por `enrollments`

### DDL inicial

```sql
CREATE DATABASE IF NOT EXISTS school_management
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE school_management;

CREATE TABLE students (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  registration_code VARCHAR(30) NOT NULL,
  full_name VARCHAR(160) NOT NULL,
  email VARCHAR(254) NULL,
  phone VARCHAR(30) NULL,
  birth_date DATE NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_students_registration_code (registration_code),
  UNIQUE KEY uk_students_email (email),
  CONSTRAINT chk_students_status CHECK (status IN ('active', 'inactive'))
) ENGINE=InnoDB;

CREATE TABLE teachers (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  employee_code VARCHAR(30) NOT NULL,
  full_name VARCHAR(160) NOT NULL,
  email VARCHAR(254) NULL,
  phone VARCHAR(30) NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_teachers_employee_code (employee_code),
  UNIQUE KEY uk_teachers_email (email),
  CONSTRAINT chk_teachers_status CHECK (status IN ('active', 'inactive'))
) ENGINE=InnoDB;

CREATE TABLE courses (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  course_code VARCHAR(30) NOT NULL,
  name VARCHAR(160) NOT NULL,
  description TEXT NULL,
  workload_hours SMALLINT UNSIGNED NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_courses_course_code (course_code),
  CONSTRAINT chk_courses_workload CHECK (workload_hours > 0),
  CONSTRAINT chk_courses_status CHECK (status IN ('active', 'inactive'))
) ENGINE=InnoDB;

CREATE TABLE school_classes (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  class_code VARCHAR(30) NOT NULL,
  course_id BIGINT UNSIGNED NOT NULL,
  teacher_id BIGINT UNSIGNED NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  max_students SMALLINT UNSIGNED NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'planned',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_school_classes_class_code (class_code),
  KEY idx_school_classes_course_id (course_id),
  KEY idx_school_classes_teacher_id (teacher_id),
  CONSTRAINT fk_school_classes_course
    FOREIGN KEY (course_id) REFERENCES courses (id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_school_classes_teacher
    FOREIGN KEY (teacher_id) REFERENCES teachers (id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT chk_school_classes_dates CHECK (end_date >= start_date),
  CONSTRAINT chk_school_classes_capacity CHECK (max_students > 0),
  CONSTRAINT chk_school_classes_status
    CHECK (status IN ('planned', 'active', 'completed', 'cancelled'))
) ENGINE=InnoDB;

CREATE TABLE enrollments (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  student_id BIGINT UNSIGNED NOT NULL,
  class_id BIGINT UNSIGNED NOT NULL,
  enrolled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(16) NOT NULL DEFAULT 'enrolled',
  final_grade DECIMAL(5,2) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_enrollments_student_class (student_id, class_id),
  KEY idx_enrollments_class_id (class_id),
  CONSTRAINT fk_enrollments_student
    FOREIGN KEY (student_id) REFERENCES students (id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_enrollments_class
    FOREIGN KEY (class_id) REFERENCES school_classes (id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT chk_enrollments_status
    CHECK (status IN ('enrolled', 'completed', 'cancelled')),
  CONSTRAINT chk_enrollments_final_grade
    CHECK (final_grade IS NULL OR final_grade BETWEEN 0 AND 100)
) ENGINE=InnoDB;
```

### Regras de integridade

- Codigos de matricula, funcionario, curso e turma sao unicos. E-mails, quando informados, tambem sao unicos por entidade.
- A combinacao aluno/turma e unica; uma mesma pessoa nao pode ser matriculada duas vezes na mesma turma.
- A API deve validar a capacidade da turma e fazer a verificacao e criacao da matricula dentro de uma transacao, evitando exceder o limite em requisicoes concorrentes.
- As chaves estrangeiras impedem apagar cursos, professores, alunos ou turmas que ainda tenham registros relacionados. Prefira inativar registros; exclusoes fisicas devem ser restritas e explicitas.
- Checks e regras de negocio devem ser validados tambem no backend. Nao dependa apenas de validacao no navegador.

## Diretrizes de arquitetura

### Backend

- Exponha uma API REST versionada sob `/api/v1`; use JSON e substantivos no plural, por exemplo `/students`, `/teachers`, `/courses`, `/classes` e `/enrollments`.
- Separe rotas/controllers, servicos de negocio, acesso a dados e schemas de entrada/saida. Mantenha regras academicas fora das rotas e dos modelos ORM.
- Use SQLAlchemy com consultas parametrizadas e Alembic para todas as alteracoes de schema. Nao altere o banco de producao manualmente.
- Valide tipos, formatos, campos obrigatorios, limites e transicoes de status. Retorne erros consistentes, sem expor stack traces ou detalhes internos.
- Implemente paginacao, ordenacao e filtros nos endpoints de listagem; limite o tamanho maximo da pagina.
- Use codigos HTTP adequados: `201` ao criar, `200` ao consultar/atualizar, `204` ao excluir, `404` quando nao existir e `409` para conflito de unicidade, capacidade ou relacionamento.
- Mantenha transacoes curtas e use rollback em falhas. Trate erros de unicidade e chaves estrangeiras como respostas de dominio compreensiveis.

### Frontend

- Organize a aplicacao AngularJS por funcionalidade, com views/controllers pequenos e servicos dedicados para chamadas HTTP.
- Centralize configuracao da API, tratamento de erros e estado de carregamento. Nao acesse o banco nem replique regras de negocio no frontend.
- Use formularios com validacao e mensagens acessiveis. Confirme operacoes destrutivas e apresente estados vazios, carregamento e falha.
- Evite inserir dados do usuario como HTML confiavel; use os mecanismos de escaping do AngularJS.

### Seguranca e configuracao

- Mantenha credenciais e chaves fora do codigo e do controle de versao; use variaveis de ambiente ou um gerenciador de segredos.
- Use usuario MySQL com privilegio minimo, TLS quando aplicavel e consultas parametrizadas.
- Se houver autenticacao, armazene apenas hashes de senha com algoritmo apropriado; aplique autorizacao por papel no backend e proteja dados pessoais, especialmente de menores.
- Configure CORS para origens conhecidas, limite e valide entradas, e registre eventos sem incluir senhas, tokens ou dados pessoais desnecessarios.
- Use HTTPS fora do ambiente local. Mantenha configuracoes distintas para desenvolvimento, testes e producao.

## Estrutura sugerida

```text
frontend/
  src/
    app/
      students/
      teachers/
      courses/
      classes/
      enrollments/
      shared/
backend/
  app/
    api/v1/
    models/
    schemas/
    services/
    repositories/
    core/
  migrations/
  tests/
```

## Qualidade e operacao

- Escreva testes unitarios para validacoes e regras de negocio, e testes de integracao para endpoints, transacoes e restricoes do MySQL.
- Cubra principalmente matricula duplicada, turma lotada, datas invalidas, referencias inexistentes e exclusao de registros relacionados.
- Use dados de teste isolados; nunca rode testes destrutivos contra dados reais.
- Registre logs estruturados e monitore erros sem gravar dados sensiveis. Inclua health check e backups testados para o banco.
- Documente endpoints via OpenAPI, mantenha migrations revisadas e execute formatacao, lint e testes no CI antes de integrar alteracoes.
