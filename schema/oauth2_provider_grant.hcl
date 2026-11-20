table "oauth2_provider_grant" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = bigint
    auto_increment = true
  }
  column "code" {
    null = false
    type = varchar(255)
  }
  column "expires" {
    null = false
    type = datetime(6)
  }
  column "redirect_uri" {
    null = false
    type = longtext
  }
  column "scope" {
    null = false
    type = longtext
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
  column "code_challenge" {
    null = false
    type = varchar(128)
  }
  column "code_challenge_method" {
    null = false
    type = varchar(10)
  }
  column "nonce" {
    null = false
    type = varchar(255)
  }
  column "claims" {
    null = false
    type = longtext
  }
  column "resource" {
    null = false
    type = json
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "oauth2_provider_gran_application_id_81923564_fk_oauth2_pr" {
    columns     = [column.application_id]
    ref_columns = [table.oauth2_provider_application.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "oauth2_provider_grant_user_id_e8f62af8_fk_auth_user_id" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "code" {
    unique  = true
    columns = [column.code]
  }
  index "oauth2_provider_grant_user_id_e8f62af8_fk_auth_user_id" {
    columns = [column.user_id]
  }
  index "oauth2_provider_gran_application_id_81923564_fk_oauth2_pr" {
    columns = [column.application_id]
  }
}
