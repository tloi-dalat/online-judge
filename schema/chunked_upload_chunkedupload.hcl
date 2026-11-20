table "chunked_upload_chunkedupload" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "upload_id" {
    null = false
    type = varchar(32)
  }
  column "file" {
    null = false
    type = varchar(255)
  }
  column "filename" {
    null = false
    type = varchar(255)
  }
  column "offset" {
    null = false
    type = bigint
  }
  column "created_on" {
    null = false
    type = datetime(6)
  }
  column "status" {
    null     = false
    type     = smallint
    unsigned = true
  }
  column "completed_on" {
    null = true
    type = datetime(6)
  }
  column "user_id" {
    null = true
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "chunked_upload_chunkedupload_user_id_70ff6dbf_fk_auth_user_id" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "chunked_upload_chunkedupload_user_id_70ff6dbf_fk_auth_user_id" {
    columns = [column.user_id]
  }
  index "upload_id" {
    unique  = true
    columns = [column.upload_id]
  }
  check "status" {
    expr = "`status` >= 0"
  }
}
