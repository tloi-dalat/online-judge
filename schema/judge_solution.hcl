table "judge_solution" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "is_public" {
    null = false
    type = bool
  }
  column "publish_on" {
    null = false
    type = datetime(6)
  }
  column "content" {
    null = false
    type = longtext
  }
  column "problem_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_solution_problem_id_44bbf556_fk_judge_problem_id" {
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
