table "oauth2_provider_idtoken" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = bigint
    auto_increment = true
  }
  column "jti" {
    null = false
    type = sql("uuid")
  }
  column "expires" {
    null = false
    type = datetime(6)
  }
  column "scope" {
    null = false
    type = longtext
  }
  column "created" {
    null = false
    type = datetime(6)
  }
  column "updated" {
    null = false
    type = datetime(6)
  }
  column "application_id" {
    null = true
    type = bigint
  }
  column "user_id" {
    null = true
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "oauth2_provider_idto_application_id_08c5ff4f_fk_oauth2_pr" {
    columns     = [column.application_id]
    ref_columns = [table.oauth2_provider_application.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "oauth2_provider_idtoken_user_id_dd512b59_fk_auth_user_id" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "jti" {
    unique  = true
    columns = [column.jti]
  }
  index "oauth2_provider_idtoken_user_id_dd512b59_fk_auth_user_id" {
    columns = [column.user_id]
  }
  index "oauth2_provider_idto_application_id_08c5ff4f_fk_oauth2_pr" {
    columns = [column.application_id]
  }
}
