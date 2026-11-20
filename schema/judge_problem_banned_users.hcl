table "judge_problem_banned_users" {
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
  column "profile_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_problem_banned_problem_id_f5f73ac2_fk_judge_pro" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_problem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_problem_banned_profile_id_4dcfff77_fk_judge_pro" {
    columns     = [column.profile_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_problem_banned_profile_id_4dcfff77_fk_judge_pro" {
    columns = [column.profile_id]
  }
  index "judge_problem_banned_users_problem_id_profile_id_068a01f9_uniq" {
    unique  = true
    columns = [column.problem_id, column.profile_id]
  }
}
