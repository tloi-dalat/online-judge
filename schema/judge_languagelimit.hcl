table "judge_languagelimit" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "time_limit" {
    null = false
    type = double
  }
  column "memory_limit" {
    null = false
    type = int
  }
  column "language_id" {
    null = false
    type = int
  }
  column "problem_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_languagelimit_language_id_b81fe043_fk_judge_language_id" {
    columns     = [column.language_id]
    ref_columns = [table.judge_language.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_languagelimit_problem_id_bb544679_fk_judge_problem_id" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_problem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_languagelimit_language_id_b81fe043_fk_judge_language_id" {
    columns = [column.language_id]
  }
  index "judge_languagelimit_problem_id_language_id_fbd3d3fc_uniq" {
    unique  = true
    columns = [column.problem_id, column.language_id]
  }
}
