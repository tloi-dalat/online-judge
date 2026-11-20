table "judge_rating" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "rank" {
    null = false
    type = int
  }
  column "rating" {
    null = false
    type = int
  }
  column "last_rated" {
    null = false
    type = datetime(6)
  }
  column "contest_id" {
    null = false
    type = int
  }
  column "participation_id" {
    null = false
    type = int
  }
  column "user_id" {
    null = false
    type = int
  }
  column "mean" {
    null = false
    type = double
  }
  column "performance" {
    null = false
    type = double
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_rating_contest_id_0e97ae8c_fk_judge_contest_id" {
    columns     = [column.contest_id]
    ref_columns = [table.judge_contest.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_rating_participation_id_c8cf9d76_fk_judge_con" {
    columns     = [column.participation_id]
    ref_columns = [table.judge_contestparticipation.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_rating_user_id_82072996_fk_judge_profile_id" {
    columns     = [column.user_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_rating_contest_id_0e97ae8c_fk_judge_contest_id" {
    columns = [column.contest_id]
  }
  index "judge_rating_last_rated_65ff05f9" {
    columns = [column.last_rated]
  }
  index "judge_rating_user_id_contest_id_461d7897_uniq" {
    unique  = true
    columns = [column.user_id, column.contest_id]
  }
  index "participation_id" {
    unique  = true
    columns = [column.participation_id]
  }
}
