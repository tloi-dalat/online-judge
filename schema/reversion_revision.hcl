table "reversion_revision" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "date_created" {
    null = false
    type = datetime(6)
  }
  column "comment" {
    null = false
    type = longtext
  }
  column "user_id" {
    null = true
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "reversion_revision_user_id_17095f45_fk_auth_user_id" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "reversion_revision_date_created_96f7c20c" {
    columns = [column.date_created]
  }
  index "reversion_revision_user_id_17095f45_fk_auth_user_id" {
    columns = [column.user_id]
  }
}
