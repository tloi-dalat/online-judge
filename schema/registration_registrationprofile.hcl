table "registration_registrationprofile" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "activation_key" {
    null = false
    type = varchar(64)
  }
  column "user_id" {
    null = false
    type = int
  }
  column "activated" {
    null = false
    type = bool
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "registration_registr_user_id_5fcbf725_fk_auth_user" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "user_id" {
    unique  = true
    columns = [column.user_id]
  }
}
