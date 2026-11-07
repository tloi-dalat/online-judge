table "impersonate_impersonationlog" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "session_key" {
    null = false
    type = varchar(40)
  }
  column "session_started_at" {
    null = true
    type = datetime(6)
  }
  column "session_ended_at" {
    null = true
    type = datetime(6)
  }
  column "impersonating_id" {
    null = false
    type = int
  }
  column "impersonator_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "impersonate_imperson_impersonating_id_afd114fc_fk_auth_user" {
    columns     = [column.impersonating_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "impersonate_imperson_impersonator_id_1ecfe8ce_fk_auth_user" {
    columns     = [column.impersonator_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "impersonate_imperson_impersonating_id_afd114fc_fk_auth_user" {
    columns = [column.impersonating_id]
  }
  index "impersonate_imperson_impersonator_id_1ecfe8ce_fk_auth_user" {
    columns = [column.impersonator_id]
  }
}
