table "judge_problemdata" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "zipfile" {
    null = true
    type = varchar(100)
  }
  column "generator" {
    null = true
    type = varchar(100)
  }
  column "output_prefix" {
    null = true
    type = int
  }
  column "output_limit" {
    null = true
    type = int
  }
  column "feedback" {
    null = false
    type = longtext
  }
  column "checker" {
    null = false
    type = varchar(10)
  }
  column "checker_args" {
    null = false
    type = longtext
  }
  column "problem_id" {
    null = false
    type = int
  }
  column "custom_checker" {
    null = true
    type = varchar(100)
  }
  column "custom_grader" {
    null = true
    type = varchar(100)
  }
  column "custom_header" {
    null = true
    type = varchar(100)
  }
  column "grader" {
    null = false
    type = varchar(30)
  }
  column "grader_args" {
    null = false
    type = longtext
  }
  column "nobigmath" {
    null = true
    type = bool
  }
  column "unicode" {
    null = true
    type = bool
  }
  column "zipfile_size" {
    null = false
    type = bigint
  }
  column "archived_size" {
    null = false
    type = bigint
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_problemdata_problem_id_d825e6f8_fk_judge_problem_id" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_problem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "problem_id" {
    unique  = true
    columns = [column.problem_id]
  }
}
