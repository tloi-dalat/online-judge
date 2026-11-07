table "django_content_type" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "app_label" {
    null = false
    type = varchar(100)
  }
  column "model" {
    null = false
    type = varchar(100)
  }
  primary_key {
    columns = [column.id]
  }
  index "django_content_type_app_label_model_76bd3d3b_uniq" {
    unique  = true
    columns = [column.app_label, column.model]
  }
}
