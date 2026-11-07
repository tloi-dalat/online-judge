table "auth_permission" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "name" {
    null = false
    type = varchar(255)
  }
  column "content_type_id" {
    null = false
    type = int
  }
  column "codename" {
    null = false
    type = varchar(100)
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "auth_permission_content_type_id_2f476e4b_fk_django_co" {
    columns     = [column.content_type_id]
    ref_columns = [table.django_content_type.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "auth_permission_content_type_id_codename_01ab375a_uniq" {
    unique  = true
    columns = [column.content_type_id, column.codename]
  }
}
