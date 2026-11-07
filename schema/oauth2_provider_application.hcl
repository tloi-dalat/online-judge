table "oauth2_provider_application" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = bigint
    auto_increment = true
  }
  column "client_id" {
    null = false
    type = varchar(255)
  }
  column "redirect_uris" {
    null = false
    type = longtext
  }
  column "client_type" {
    null = false
    type = varchar(32)
  }
  column "authorization_grant_type" {
    null = false
    type = varchar(44)
  }
  column "client_secret" {
    null = false
    type = varchar(255)
  }
  column "name" {
    null = false
    type = varchar(255)
  }
  column "user_id" {
    null = true
    type = int
  }
  column "skip_authorization" {
    null = false
    type = bool
  }
  column "created" {
    null = false
    type = datetime(6)
  }
  column "updated" {
    null = false
    type = datetime(6)
  }
  column "algorithm" {
    null = false
    type = varchar(5)
  }
  column "post_logout_redirect_uris" {
    null = false
    type = longtext
  }
  column "hash_client_secret" {
    null = false
    type = bool
  }
  column "allowed_origins" {
    null = false
    type = longtext
  }
  column "registration_source" {
    null = false
    type = varchar(32)
  }
  column "cimd_expires_at" {
    null = true
    type = datetime(6)
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "oauth2_provider_application_user_id_79829054_fk_auth_user_id" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "client_id" {
    unique  = true
    columns = [column.client_id]
  }
  index "oauth2_provider_application_client_secret_53133678" {
    columns = [column.client_secret]
  }
  index "oauth2_provider_application_user_id_79829054_fk_auth_user_id" {
    columns = [column.user_id]
  }
}
