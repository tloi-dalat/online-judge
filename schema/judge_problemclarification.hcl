table "judge_problemclarification" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "description" {
    null = false
    type = longtext
  }
  column "date" {
    null = false
    type = datetime(6)
  }
  column "problem_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_problemclarifi_problem_id_3d9eb049_fk_judge_pro" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_problem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_problemclarifi_problem_id_3d9eb049_fk_judge_pro" {
    columns = [column.problem_id]
  }
}
