table "judge_profile" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "about" {
    null = true
    type = longtext
  }
  column "timezone" {
    null = false
    type = varchar(50)
  }
  column "points" {
    null = false
    type = double
  }
  column "performance_points" {
    null = false
    type = double
  }
  column "problem_count" {
    null = false
    type = int
  }
  column "ace_theme" {
    null = false
    type = varchar(30)
  }
  column "last_access" {
    null = false
    type = datetime(6)
  }
  column "ip" {
    null = true
    type = char(39)
  }
  column "display_rank" {
    null = false
    type = varchar(10)
  }
  column "mute" {
    null = false
    type = bool
  }
  column "is_unlisted" {
    null = false
    type = bool
  }
  column "rating" {
    null = true
    type = int
  }
  column "user_script" {
    null = false
    type = longtext
  }
  column "math_engine" {
    null = false
    type = varchar(4)
  }
  column "is_totp_enabled" {
    null = false
    type = bool
  }
  column "totp_key" {
    null = true
    type = longblob
  }
  column "notes" {
    null = true
    type = longtext
  }
  column "current_contest_id" {
    null = true
    type = int
  }
  column "language_id" {
    null = false
    type = int
  }
  column "user_id" {
    null = false
    type = int
  }
  column "api_token" {
    null = true
    type = varchar(64)
  }
  column "is_webauthn_enabled" {
    null = false
    type = bool
  }
  column "data_last_downloaded" {
    null = true
    type = datetime(6)
  }
  column "scratch_codes" {
    null = true
    type = longblob
  }
  column "contribution_points" {
    null = false
    type = int
  }
  column "allow_tagging" {
    null = false
    type = bool
  }
  column "last_totp_timecode" {
    null = false
    type = int
  }
  column "ban_reason" {
    null = true
    type = longtext
  }
  column "username_display_override" {
    null = false
    type = varchar(100)
  }
  column "display_badge_id" {
    null = true
    type = int
  }
  column "site_theme" {
    null = false
    type = varchar(10)
  }
  column "vnoj_points" {
    null = false
    type = int
  }
  column "ip_auth" {
    null = true
    type = char(39)
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_profile_current_contest_id_ca595142_fk_judge_con" {
    columns     = [column.current_contest_id]
    ref_columns = [table.judge_contestparticipation.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_profile_display_badge_id_dc30ad34_fk_judge_badge_id" {
    columns     = [column.display_badge_id]
    ref_columns = [table.judge_badge.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_profile_language_id_87d3cab1_fk_judge_language_id" {
    columns     = [column.language_id]
    ref_columns = [table.judge_language.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_profile_user_id_b62d6977_fk_auth_user_id" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "current_contest_id" {
    unique  = true
    columns = [column.current_contest_id]
  }
  index "ip_auth" {
    unique  = true
    columns = [column.ip_auth]
  }
  index "judge_profile_display_badge_id_dc30ad34_fk_judge_badge_id" {
    columns = [column.display_badge_id]
  }
  index "judge_profile_language_id_87d3cab1_fk_judge_language_id" {
    columns = [column.language_id]
  }
  index "judge_profi_is_unli_1410d8_idx" {
    on {
      column = column.is_unlisted
    }
    on {
      desc   = true
      column = column.performance_points
    }
  }
  index "judge_profi_is_unli_171bf3_idx" {
    on {
      column = column.is_unlisted
    }
    on {
      desc   = true
      column = column.problem_count
    }
  }
  index "judge_profi_is_unli_bcf16a_idx" {
    on {
      column = column.is_unlisted
    }
    on {
      desc   = true
      column = column.rating
    }
  }
  index "judge_profi_is_unli_d31e5b_idx" {
    on {
      column = column.is_unlisted
    }
    on {
      desc   = true
      column = column.contribution_points
    }
  }
  index "user_id" {
    unique  = true
    columns = [column.user_id]
  }
}
