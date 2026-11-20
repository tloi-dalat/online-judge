table "judge_submission" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "date" {
    null = false
    type = datetime(6)
  }
  column "time" {
    null = true
    type = double
  }
  column "memory" {
    null = true
    type = double
  }
  column "points" {
    null = true
    type = double
  }
  column "status" {
    null = false
    type = varchar(2)
  }
  column "result" {
    null = true
    type = varchar(3)
  }
  column "error" {
    null = true
    type = longtext
  }
  column "current_testcase" {
    null = false
    type = int
  }
  column "batch" {
    null = false
    type = bool
  }
  column "case_points" {
    null = false
    type = double
  }
  column "case_total" {
    null = false
    type = double
  }
  column "is_pretested" {
    null = false
    type = bool
  }
  column "judged_on_id" {
    null = true
    type = int
  }
  column "language_id" {
    null = false
    type = int
  }
  column "problem_id" {
    null = false
    type = int
  }
  column "user_id" {
    null = false
    type = int
  }
  column "contest_object_id" {
    null = true
    type = int
  }
  column "judged_date" {
    null = true
    type = datetime(6)
  }
  column "locked_after" {
    null = true
    type = datetime(6)
  }
  column "rejudged_date" {
    null = true
    type = datetime(6)
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_submission_contest_object_id_c5586240_fk_judge_contest_id" {
    columns     = [column.contest_object_id]
    ref_columns = [table.judge_contest.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_submission_judged_on_id_ef7707ef_fk_judge_judge_id" {
    columns     = [column.judged_on_id]
    ref_columns = [table.judge_judge.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_submission_language_id_48a75504_fk_judge_language_id" {
    columns     = [column.language_id]
    ref_columns = [table.judge_language.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_submission_problem_id_d2fabe38_fk_judge_problem_id" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_problem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_submission_user_id_9764487f_fk_judge_profile_id" {
    columns     = [column.user_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_submission_date_14094309" {
    columns = [column.date]
  }
  index "judge_submission_judged_on_id_ef7707ef_fk_judge_judge_id" {
    columns = [column.judged_on_id]
  }
  index "judge_submission_status_3f629ced" {
    columns = [column.status]
  }
  index "judge_submi_contest_59fbe3_idx" {
    on {
      column = column.contest_object_id
    }
    on {
      column = column.problem_id
    }
    on {
      column = column.user_id
    }
    on {
      desc   = true
      column = column.points
    }
    on {
      desc   = true
      column = column.time
    }
  }
  index "judge_submi_contest_bc50a1_idx" {
    on {
      column = column.contest_object_id
    }
    on {
      desc   = true
      column = column.id
    }
  }
  index "judge_submi_contest_fb7afc_idx" {
    on {
      column = column.contest_object_id
    }
    on {
      column = column.user_id
    }
    on {
      desc   = true
      column = column.id
    }
  }
  index "judge_submi_languag_380ab4_idx" {
    columns = [column.language_id, column.problem_id, column.result]
  }
  index "judge_submi_languag_dfe850_idx" {
    on {
      column = column.language_id
    }
    on {
      desc   = true
      column = column.id
    }
  }
  index "judge_submi_problem_1d8475_idx" {
    on {
      column = column.problem_id
    }
    on {
      desc   = true
      column = column.date
    }
  }
  index "judge_submi_problem_49f8ec_idx" {
    columns = [column.problem_id, column.result]
  }
  index "judge_submi_problem_801afc_idx" {
    on {
      column = column.problem_id
    }
    on {
      desc   = true
      column = column.id
    }
  }
  index "judge_submi_problem_8d5e0a_idx" {
    on {
      column = column.problem_id
    }
    on {
      column = column.user_id
    }
    on {
      desc   = true
      column = column.points
    }
    on {
      desc   = true
      column = column.time
    }
  }
  index "judge_submi_result_7a005c_idx" {
    on {
      column = column.result
    }
    on {
      desc   = true
      column = column.id
    }
  }
  index "judge_submi_result_a77e42_idx" {
    columns = [column.result, column.problem_id]
  }
  index "judge_submi_result_ba9a62_idx" {
    on {
      column = column.result
    }
    on {
      column = column.language_id
    }
    on {
      desc   = true
      column = column.id
    }
  }
  index "judge_submi_user_id_52a3e2_idx" {
    on {
      column = column.user_id
    }
    on {
      desc   = true
      column = column.id
    }
  }
  index "judge_submi_user_id_650db3_idx" {
    columns = [column.user_id, column.problem_id, column.result]
  }
  index "judge_submi_user_id_a309f7_idx" {
    columns = [column.user_id, column.date]
  }
  index "judge_submi_user_id_ec9a4b_idx" {
    columns = [column.user_id, column.result]
  }
}
