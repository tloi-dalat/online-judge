table "judge_profile_badges" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "profile_id" {
    null = false
    type = int
  }
  column "badge_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_profile_badges_badge_id_ec2e6035_fk_judge_badge_id" {
    columns     = [column.badge_id]
    ref_columns = [table.judge_badge.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_profile_badges_profile_id_be0cef45_fk_judge_profile_id" {
    columns     = [column.profile_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_profile_badges_badge_id_ec2e6035_fk_judge_badge_id" {
    columns = [column.badge_id]
  }
  index "judge_profile_badges_profile_id_badge_id_5e1e5072_uniq" {
    unique  = true
    columns = [column.profile_id, column.badge_id]
  }
}
