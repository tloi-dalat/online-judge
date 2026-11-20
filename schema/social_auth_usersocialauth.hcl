table "social_auth_usersocialauth" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = bigint
    auto_increment = true
  }
  column "provider" {
    null = false
    type = varchar(32)
  }
  column "uid" {
    null = false
    type = varchar(255)
  }
  column "user_id" {
    null = false
    type = int
  }
  column "created" {
    null = false
    type = datetime(6)
  }
  column "modified" {
    null = false
    type = datetime(6)
  }
  column "extra_data" {
    null = false
    type = json
  }
  column "id_key" {
    null = false
    type = varchar(255)
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "social_auth_usersocialauth_user_id_17d28448_fk_auth_user_id" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "social_auth_usersocialauth_provider_uid_e6b5e668_uniq" {
    unique  = true
    columns = [column.provider, column.uid]
  }
  index "social_auth_usersocialauth_uid_796e51dc" {
    columns = [column.uid]
  }
  index "social_auth_usersocialauth_user_id_17d28448_fk_auth_user_id" {
    columns = [column.user_id]
  }
  check "user_social_auth_uid_required" {
    expr = "`uid` <> ''"
  }
}
