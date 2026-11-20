table "judge_contest_authors" {
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
  foreign_key "judge_contest_organizers_contest_id_266a7461_fk_judge_contest_id" {
    columns     = [column.contest_id]
    ref_columns = [table.judge_contest.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_contest_organizers_profile_id_fe54f029_fk_judge_profile_id" {
    columns     = [column.profile_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_contest_organizers_contest_id_profile_id_35f37708_uniq" {
    unique  = true
    columns = [column.contest_id, column.profile_id]
  }
  index "judge_contest_organizers_profile_id_fe54f029_fk_judge_profile_id" {
    columns = [column.profile_id]
  }
}
