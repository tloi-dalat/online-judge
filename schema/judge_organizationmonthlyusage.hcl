table "judge_organizationmonthlyusage" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "time" {
    null = false
    type = date
  }
  column "consumed_credit" {
    null = false
    type = double
  }
  column "organization_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_organizationmo_organization_id_df11ac98_fk_judge_org" {
    columns     = [column.organization_id]
    ref_columns = [table.judge_organization.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_organizationmonthl_organization_id_time_2bfbd371_uniq" {
    unique  = true
    columns = [column.organization_id, column.time]
  }
}
