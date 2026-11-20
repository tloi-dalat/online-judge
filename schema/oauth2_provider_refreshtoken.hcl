table "oauth2_provider_refreshtoken" {
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
  column "access_token_id" {
    null = true
    type = bigint
  }
  column "application_id" {
    null = false
    type = bigint
  }
  column "user_id" {
    null = false
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
  column "revoked" {
    null = true
    type = datetime(6)
  }
  column "token_family" {
    null = true
    type = sql("uuid")
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
  foreign_key "oauth2_provider_refr_access_token_id_775e84e8_fk_oauth2_pr" {
    columns     = [column.access_token_id]
    ref_columns = [table.oauth2_provider_accesstoken.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "oauth2_provider_refr_application_id_2d1c311b_fk_oauth2_pr" {
    columns     = [column.application_id]
    ref_columns = [table.oauth2_provider_application.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "oauth2_provider_refreshtoken_user_id_da837fce_fk_auth_user_id" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "access_token_id" {
    unique  = true
    columns = [column.access_token_id]
  }
  index "oauth2_provider_refreshtoken_user_id_da837fce_fk_auth_user_id" {
    columns = [column.user_id]
  }
  index "oauth2_provider_refresht_token_checksum_revoked_46c81d1d_uniq" {
    unique  = true
    columns = [column.token_checksum, column.revoked]
  }
  index "oauth2_provider_refr_application_id_2d1c311b_fk_oauth2_pr" {
    columns = [column.application_id]
  }
  index "oauth2_prov_token_f_996e8a_idx" {
    columns = [column.token_family]
  }
}
