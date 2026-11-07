table "judge_problem_allowed_languages" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "problem_id" {
    null = false
    type = int
  }
  column "language_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_problem_allowe_language_id_67ad291b_fk_judge_lan" {
    columns     = [column.language_id]
    ref_columns = [table.judge_language.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_problem_allowe_problem_id_1020494d_fk_judge_pro" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_problem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_problem_allowed_la_problem_id_language_id_f6265ceb_uniq" {
    unique  = true
    columns = [column.problem_id, column.language_id]
  }
  index "judge_problem_allowe_language_id_67ad291b_fk_judge_lan" {
    columns = [column.language_id]
  }
}
