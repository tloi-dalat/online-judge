table "judge_contestparticipation" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "start" {
    null = false
    type = datetime(6)
  }
  column "score" {
    null = false
    type = double
  }
  column "cumtime" {
    null     = false
    type     = int
    unsigned = true
  }
  column "virtual" {
    null = false
    type = int
  }
  column "format_data" {
    null = true
    type = longtext
  }
  column "contest_id" {
    null = false
    type = int
  }
  column "user_id" {
    null = false
    type = int
  }
  column "is_disqualified" {
    null = false
    type = bool
  }
  column "tiebreaker" {
    null = false
    type = double
  }
  column "frozen_cumtime" {
    null     = false
    type     = int
    unsigned = true
  }
  column "frozen_score" {
    null = false
    type = double
  }
  column "frozen_tiebreaker" {
    null = false
    type = double
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_contestpartici_contest_id_ab097823_fk_judge_con" {
    columns     = [column.contest_id]
    ref_columns = [table.judge_contest.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_contestparticipation_user_id_5896ee2e_fk_judge_profile_id" {
    columns     = [column.user_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_contestparticipation_frozen_score_caac9939" {
    columns = [column.frozen_score]
  }
  index "judge_contestparticipation_score_4098b84f" {
    columns = [column.score]
  }
  index "judge_contestparticipation_user_id_5896ee2e_fk_judge_profile_id" {
    columns = [column.user_id]
  }
  index "judge_contestparticipati_contest_id_user_id_virtu_dc257b0c_uniq" {
    unique  = true
    columns = [column.contest_id, column.user_id, column.virtual]
  }
  check "cumtime" {
    expr = "`cumtime` >= 0"
  }
  check "frozen_cumtime" {
    expr = "`frozen_cumtime` >= 0"
  }
}
