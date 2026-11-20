table "judge_profile_organizations" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "sort_value" {
    null = false
    type = int
  }
  column "profile_id" {
    null = false
    type = int
  }
  column "organization_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_profile_organi_organization_id_da2a4d7d_fk_judge_org" {
    columns     = [column.organization_id]
    ref_columns = [table.judge_organization.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_profile_organi_profile_id_6b79e464_fk_judge_pro" {
    columns     = [column.profile_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_profile_organizati_profile_id_organization__39a6d8b0_uniq" {
    unique  = true
    columns = [column.profile_id, column.organization_id]
  }
  index "judge_profile_organi_organization_id_da2a4d7d_fk_judge_org" {
    columns = [column.organization_id]
  }
}
