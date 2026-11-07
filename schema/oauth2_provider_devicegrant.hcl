table "oauth2_provider_devicegrant" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = bigint
    auto_increment = true
  }
  column "device_code" {
    null = false
    type = varchar(100)
  }
  column "user_code" {
    null = false
    type = varchar(100)
  }
  column "scope" {
    null = false
    type = longtext
  }
  column "interval" {
    null = false
    type = int
  }
  column "expires" {
    null = false
    type = datetime(6)
  }
  column "status" {
    null = false
    type = varchar(64)
  }
  column "client_id" {
    null = false
    type = varchar(100)
  }
  column "last_checked" {
    null = false
    type = datetime(6)
  }
  column "user_id" {
    null = true
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "oauth2_provider_devicegrant_user_id_1cec5156_fk_auth_user_id" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "oauth2_provider_devicegrant_client_id_229dd06d" {
    columns = [column.client_id]
  }
  index "oauth2_provider_devicegrant_unique_device_code" {
    unique  = true
    columns = [column.device_code]
  }
  index "oauth2_provider_devicegrant_user_id_1cec5156_fk_auth_user_id" {
    columns = [column.user_id]
  }
}
