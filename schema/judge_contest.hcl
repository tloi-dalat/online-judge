table "judge_contest" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "key" {
    null = false
    type = varchar(32)
  }
  column "name" {
    null = false
    type = varchar(100)
  }
  column "description" {
    null = false
    type = longtext
  }
  column "start_time" {
    null = false
    type = datetime(6)
  }
  column "end_time" {
    null = false
    type = datetime(6)
  }
  column "time_limit" {
    null = true
    type = bigint
  }
  column "is_visible" {
    null = false
    type = bool
  }
  column "is_rated" {
    null = false
    type = bool
  }
  column "use_clarifications" {
    null = false
    type = bool
  }
  column "rate_all" {
    null = false
    type = bool
  }
  column "is_private" {
    null = false
    type = bool
  }
  column "hide_problem_tags" {
    null = false
    type = bool
  }
  column "run_pretests_only" {
    null = false
    type = bool
  }
  column "og_image" {
    null = false
    type = varchar(150)
  }
  column "logo_override_image" {
    null = false
    type = varchar(150)
  }
  column "user_count" {
    null = false
    type = int
  }
  column "summary" {
    null = false
    type = longtext
  }
  column "access_code" {
    null = false
    type = varchar(255)
  }
  column "format_name" {
    null = false
    type = varchar(32)
  }
  column "format_config" {
    null = true
    type = longtext
  }
  column "rating_ceiling" {
    null = true
    type = int
  }
  column "rating_floor" {
    null = true
    type = int
  }
  column "is_organization_private" {
    null = false
    type = bool
  }
  column "problem_label_script" {
    null = false
    type = longtext
  }
  column "points_precision" {
    null = false
    type = int
  }
  column "scoreboard_visibility" {
    null = false
    type = varchar(1)
  }
  column "virtual_count" {
    null = false
    type = int
  }
  column "locked_after" {
    null = true
    type = datetime(6)
  }
  column "hide_problem_authors" {
    null = false
    type = bool
  }
  column "csv_ranking" {
    null = false
    type = longtext
  }
  column "show_short_display" {
    null = false
    type = bool
  }
  column "push_announcements" {
    null = false
    type = bool
  }
  column "frozen_last_minutes" {
    null = false
    type = int
  }
  column "show_submission_list" {
    null = false
    type = bool
  }
  column "scoreboard_cache_timeout" {
    null     = false
    type     = int
    unsigned = true
  }
  column "data_last_downloaded" {
    null = true
    type = datetime(6)
  }
  column "disallow_virtual" {
    null = false
    type = bool
  }
  column "ranking_access_code" {
    null = false
    type = varchar(255)
  }
  column "registration_end" {
    null = true
    type = datetime(6)
  }
  column "registration_start" {
    null = true
    type = datetime(6)
  }
  column "rate_disqualified" {
    null = false
    type = bool
  }
  column "organization_id" {
    null = true
    type = int
  }
  column "terms" {
    null = false
    type = longtext
  }
  column "unfreeze_time" {
    null = true
    type = datetime(6)
  }
  column "replay_version" {
    null     = false
    type     = int
    unsigned = true
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_contest_organization_id_a5f8f5df_fk_judge_organization_id" {
    columns     = [column.organization_id]
    ref_columns = [table.judge_organization.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_contest_end_time_f0179778" {
    columns = [column.end_time]
  }
  index "judge_contest_name_23b5c29c" {
    columns = [column.name]
  }
  index "judge_contest_organization_id_a5f8f5df_fk_judge_organization_id" {
    columns = [column.organization_id]
  }
  index "judge_contest_start_time_8dd80870" {
    columns = [column.start_time]
  }
  index "judge_conte_end_tim_c5e323_idx" {
    on {
      desc   = true
      column = column.end_time
    }
    on {
      column = column.key
    }
  }
  index "key" {
    unique  = true
    columns = [column.key]
  }
  check "replay_version" {
    expr = "`replay_version` >= 0"
  }
  check "scoreboard_cache_timeout" {
    expr = "`scoreboard_cache_timeout` >= 0"
  }
}
