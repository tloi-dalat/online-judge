table "judge_problem" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "code" {
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
  column "time_limit" {
    null = false
    type = double
  }
  column "memory_limit" {
    null     = false
    type     = int
    unsigned = true
  }
  column "short_circuit" {
    null = false
    type = bool
  }
  column "points" {
    null = false
    type = double
  }
  column "partial" {
    null = false
    type = bool
  }
  column "is_public" {
    null = false
    type = bool
  }
  column "is_manually_managed" {
    null = false
    type = bool
  }
  column "date" {
    null = true
    type = datetime(6)
  }
  column "og_image" {
    null = false
    type = varchar(150)
  }
  column "summary" {
    null = false
    type = longtext
  }
  column "user_count" {
    null = false
    type = int
  }
  column "ac_rate" {
    null = false
    type = double
  }
  column "is_organization_private" {
    null = false
    type = bool
  }
  column "group_id" {
    null = false
    type = int
  }
  column "license_id" {
    null = true
    type = int
  }
  column "is_full_markup" {
    null = false
    type = bool
  }
  column "pdf_url" {
    null = false
    type = varchar(200)
  }
  column "source" {
    null = false
    type = varchar(200)
  }
  column "submission_source_visibility_mode" {
    null = false
    type = varchar(1)
  }
  column "testcase_visibility_mode" {
    null = false
    type = varchar(1)
  }
  column "allow_view_feedback" {
    null = false
    type = bool
  }
  column "testcase_result_visibility_mode" {
    null = false
    type = varchar(1)
  }
  column "organization_id" {
    null = true
    type = int
  }
  column "deleted_at" {
    null = true
    type = datetime(6)
  }
  column "archived_at" {
    null = true
    type = datetime(6)
  }
  column "storage" {
    null = false
    type = varchar(100)
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_problem_group_id_1b7ca650_fk_judge_problemgroup_id" {
    columns     = [column.group_id]
    ref_columns = [table.judge_problemgroup.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_problem_license_id_32ca8b1a_fk_judge_license_id" {
    columns     = [column.license_id]
    ref_columns = [table.judge_license.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_problem_organization_id_e2507d90_fk_judge_organization_id" {
    columns     = [column.organization_id]
    ref_columns = [table.judge_organization.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "code" {
    unique  = true
    columns = [column.code]
  }
  index "judge_problem_date_f1f729a4" {
    columns = [column.date]
  }
  index "judge_problem_deleted_at_bae46a51" {
    columns = [column.deleted_at]
  }
  index "judge_problem_group_id_1b7ca650_fk_judge_problemgroup_id" {
    columns = [column.group_id]
  }
  index "judge_problem_is_manually_managed_56d3b634" {
    columns = [column.is_manually_managed]
  }
  index "judge_problem_license_id_32ca8b1a_fk_judge_license_id" {
    columns = [column.license_id]
  }
  index "judge_problem_name_c48e19b2" {
    columns = [column.name]
  }
  index "judge_problem_source_8a196bf6" {
    columns = [column.source]
  }
  index "judge_probl_is_publ_b00d80_idx" {
    on {
      column = column.is_public
    }
    on {
      column = column.is_organization_private
    }
    on {
      desc   = true
      column = column.date
    }
  }
  index "judge_probl_organiz_0d1c92_idx" {
    on {
      column = column.organization_id
    }
    on {
      desc   = true
      column = column.archived_at
    }
  }
  index "judge_probl_organiz_61d146_idx" {
    columns = [column.organization_id, column.date]
  }
  check "judge_problem_memory_limit_a129f739_check" {
    expr = "`memory_limit` >= 0"
  }
}
