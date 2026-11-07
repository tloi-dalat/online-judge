table "django_admin_log" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "action_time" {
    null = false
    type = datetime(6)
  }
  column "object_id" {
    null = true
    type = longtext
  }
  column "object_repr" {
    null = false
    type = varchar(200)
  }
  column "action_flag" {
    null     = false
    type     = smallint
    unsigned = true
  }
  column "change_message" {
    null = false
    type = longtext
  }
  column "content_type_id" {
    null = true
    type = int
  }
  column "user_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "django_admin_log_content_type_id_c4bce8eb_fk_django_co" {
    columns     = [column.content_type_id]
    ref_columns = [table.django_content_type.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "django_admin_log_user_id_c564eba6_fk_auth_user_id" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "django_admin_log_content_type_id_c4bce8eb_fk_django_co" {
    columns = [column.content_type_id]
  }
  index "django_admin_log_user_id_c564eba6_fk_auth_user_id" {
    columns = [column.user_id]
  }
  check "action_flag" {
    expr = "`action_flag` >= 0"
  }
}
