table "oauth2_provider_accesstoken" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = bigint
    auto_increment = true
  }
  column "token" {
    null = false
    type = longtext
  }
  column "expires" {
    null = false
    type = datetime(6)
  }
  column "scope" {
    null = false
    type = longtext
  }
  column "application_id" {
    null = true
    type = bigint
  }
  column "user_id" {
    null = true
    type = int
  }
  column "created" {
    null = false
    type = datetime(6)
  }
  column "updated" {
    null = false
    type = datetime(6)
  }
  column "source_refresh_token_id" {
    null = true
    type = bigint
  }
  column "id_token_id" {
    null = true
    type = bigint
  }
  column "token_checksum" {
    null = false
    type = varchar(64)
  }
  column "resource" {
    null = false
    type = json
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "oauth2_provider_acce_application_id_b22886e1_fk_oauth2_pr" {
    columns     = [column.application_id]
    ref_columns = [table.oauth2_provider_application.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "oauth2_provider_acce_id_token_id_85db651b_fk_oauth2_pr" {
    columns     = [column.id_token_id]
    ref_columns = [table.oauth2_provider_idtoken.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "oauth2_provider_acce_source_refresh_token_e66fbc72_fk_oauth2_pr" {
    columns     = [column.source_refresh_token_id]
    ref_columns = [table.oauth2_provider_refreshtoken.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "oauth2_provider_accesstoken_user_id_6e4c9a65_fk_auth_user_id" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "id_token_id" {
    unique  = true
    columns = [column.id_token_id]
  }
  index "oauth2_provider_accesstoken_token_checksum_85319a26_uniq" {
    unique  = true
    columns = [column.token_checksum]
  }
  index "oauth2_provider_accesstoken_user_id_6e4c9a65_fk_auth_user_id" {
    columns = [column.user_id]
  }
  index "oauth2_provider_acce_application_id_b22886e1_fk_oauth2_pr" {
    columns = [column.application_id]
  }
  index "source_refresh_token_id" {
    unique  = true
    columns = [column.source_refresh_token_id]
  }
}
