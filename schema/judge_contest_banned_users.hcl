table "judge_contest_banned_users" {
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
  foreign_key "judge_contest_banned_contest_id_14d2192a_fk_judge_con" {
    columns     = [column.contest_id]
    ref_columns = [table.judge_contest.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_contest_banned_profile_id_ae615b59_fk_judge_pro" {
    columns     = [column.profile_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_contest_banned_profile_id_ae615b59_fk_judge_pro" {
    columns = [column.profile_id]
  }
  index "judge_contest_banned_users_contest_id_profile_id_b0570b33_uniq" {
    unique  = true
    columns = [column.contest_id, column.profile_id]
  }
}
