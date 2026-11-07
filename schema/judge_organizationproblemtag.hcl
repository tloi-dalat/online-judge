table "judge_organizationproblemtag" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "name" {
    null = false
    type = varchar(50)
  }
  column "organization_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_organizationpr_organization_id_6bde960d_fk_judge_org" {
    columns     = [column.organization_id]
    ref_columns = [table.judge_organization.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_organizationproblemtag_organization_id_name_153f9d94_uniq" {
    unique  = true
    columns = [column.organization_id, column.name]
  }
}
