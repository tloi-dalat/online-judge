table "judge_solution_authors" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "solution_id" {
    null = false
    type = int
  }
  column "profile_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_solution_authors_profile_id_685bd965_fk_judge_profile_id" {
    columns     = [column.profile_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_solution_authors_solution_id_eab0d5e6_fk_judge_solution_id" {
    columns     = [column.solution_id]
    ref_columns = [table.judge_solution.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_solution_authors_profile_id_685bd965_fk_judge_profile_id" {
    columns = [column.profile_id]
  }
  index "judge_solution_authors_solution_id_profile_id_e45470e0_uniq" {
    unique  = true
    columns = [column.solution_id, column.profile_id]
  }
}
