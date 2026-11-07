table "judge_problem_testers" {
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
  foreign_key "judge_problem_testers_problem_id_0796300b_fk_judge_problem_id" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_problem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_problem_testers_profile_id_dadcfbad_fk_judge_profile_id" {
    columns     = [column.profile_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_problem_testers_problem_id_profile_id_3ff28b2a_uniq" {
    unique  = true
    columns = [column.problem_id, column.profile_id]
  }
  index "judge_problem_testers_profile_id_dadcfbad_fk_judge_profile_id" {
    columns = [column.profile_id]
  }
}
