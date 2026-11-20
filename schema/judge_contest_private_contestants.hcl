table "judge_contest_private_contestants" {
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
  foreign_key "judge_contest_privat_contest_id_a30921fe_fk_judge_con" {
    columns     = [column.contest_id]
    ref_columns = [table.judge_contest.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_contest_privat_profile_id_34a11bc5_fk_judge_pro" {
    columns     = [column.profile_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_contest_private_co_contest_id_profile_id_ef23dc8d_uniq" {
    unique  = true
    columns = [column.contest_id, column.profile_id]
  }
  index "judge_contest_privat_profile_id_34a11bc5_fk_judge_pro" {
    columns = [column.profile_id]
  }
}
