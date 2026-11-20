table "judge_contest_curators" {
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
  foreign_key "judge_contest_curators_contest_id_06a850b7_fk_judge_contest_id" {
    columns     = [column.contest_id]
    ref_columns = [table.judge_contest.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_contest_curators_profile_id_73c4ada2_fk_judge_profile_id" {
    columns     = [column.profile_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_contest_curators_contest_id_profile_id_6bcc5bc0_uniq" {
    unique  = true
    columns = [column.contest_id, column.profile_id]
  }
  index "judge_contest_curators_profile_id_73c4ada2_fk_judge_profile_id" {
    columns = [column.profile_id]
  }
}
