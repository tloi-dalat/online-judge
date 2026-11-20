table "judge_organizationrequest" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "time" {
    null = false
    type = datetime(6)
  }
  column "state" {
    null = false
    type = varchar(1)
  }
  column "reason" {
    null = false
    type = longtext
  }
  column "organization_id" {
    null = false
    type = int
  }
  column "user_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_organizationre_organization_id_e2ab3e9a_fk_judge_org" {
    columns     = [column.organization_id]
    ref_columns = [table.judge_organization.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_organizationrequest_user_id_b721da81_fk_judge_profile_id" {
    columns     = [column.user_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_organizationrequest_user_id_b721da81_fk_judge_profile_id" {
    columns = [column.user_id]
  }
  index "judge_organizationre_organization_id_e2ab3e9a_fk_judge_org" {
    columns = [column.organization_id]
  }
}
