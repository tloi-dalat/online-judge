table "judge_contest_rate_exclude" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "contest_id" {
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
  foreign_key "judge_contest_rate_e_contest_id_30174232_fk_judge_con" {
    columns     = [column.contest_id]
    ref_columns = [table.judge_contest.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_contest_rate_e_profile_id_6c9400fa_fk_judge_pro" {
    columns     = [column.profile_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_contest_rate_exclude_contest_id_profile_id_2b34d7a9_uniq" {
    unique  = true
    columns = [column.contest_id, column.profile_id]
  }
  index "judge_contest_rate_e_profile_id_6c9400fa_fk_judge_pro" {
    columns = [column.profile_id]
  }
}
