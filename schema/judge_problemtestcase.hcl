table "judge_problemtestcase" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "order" {
    null = false
    type = int
  }
  column "type" {
    null = false
    type = varchar(1)
  }
  column "input_file" {
    null = false
    type = varchar(100)
  }
  column "output_file" {
    null = false
    type = varchar(100)
  }
  column "generator_args" {
    null = false
    type = longtext
  }
  column "points" {
    null = true
    type = int
  }
  column "is_pretest" {
    null = false
    type = bool
  }
  column "output_prefix" {
    null = true
    type = int
  }
  column "output_limit" {
    null = true
    type = int
  }
  column "checker" {
    null = false
    type = varchar(10)
  }
  column "checker_args" {
    null = false
    type = longtext
  }
  column "dataset_id" {
    null = false
    type = int
  }
  column "is_example" {
    null = false
    type = bool
  }
  column "batch_dependencies" {
    null = false
    type = longtext
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_problemtestcase_dataset_id_964229fd_fk_judge_problem_id" {
    columns     = [column.dataset_id]
    ref_columns = [table.judge_problem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_problemtestcase_dataset_id_964229fd_fk_judge_problem_id" {
    columns = [column.dataset_id]
  }
}
