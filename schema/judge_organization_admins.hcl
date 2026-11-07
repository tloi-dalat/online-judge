table "judge_organization_admins" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "organization_id" {
    null = false
    type = int
  }
  column "profile_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_organization_a_organization_id_b2125a57_fk_judge_org" {
    columns     = [column.organization_id]
    ref_columns = [table.judge_organization.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_organization_a_profile_id_b5559f11_fk_judge_pro" {
    columns     = [column.profile_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_organization_admin_organization_id_profile__7528cebe_uniq" {
    unique  = true
    columns = [column.organization_id, column.profile_id]
  }
  index "judge_organization_a_profile_id_b5559f11_fk_judge_pro" {
    columns = [column.profile_id]
  }
}
