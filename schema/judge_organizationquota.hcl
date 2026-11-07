table "judge_organizationquota" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "start_date" {
    null = false
    type = date
  }
  column "end_date" {
    null = false
    type = date
  }
  column "added_problems" {
    null = false
    type = int
  }
  column "added_storage" {
    null = false
    type = bigint
  }
  column "organization_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_organizationqu_organization_id_b5134c8f_fk_judge_org" {
    columns     = [column.organization_id]
    ref_columns = [table.judge_organization.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_organizationqu_organization_id_b5134c8f_fk_judge_org" {
    columns = [column.organization_id]
  }
}
