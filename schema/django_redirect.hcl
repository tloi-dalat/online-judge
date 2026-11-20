table "django_redirect" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "site_id" {
    null = false
    type = int
  }
  column "old_path" {
    null = false
    type = varchar(200)
  }
  column "new_path" {
    null = false
    type = varchar(200)
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "django_redirect_site_id_c3e37341_fk_django_site_id" {
    columns     = [column.site_id]
    ref_columns = [table.django_site.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "django_redirect_old_path_c6cc94d3" {
    columns = [column.old_path]
  }
  index "django_redirect_site_id_old_path_ac5dd16b_uniq" {
    unique  = true
    columns = [column.site_id, column.old_path]
  }
}
