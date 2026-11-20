table "django_session" {
  schema = schema.online_judge
  column "session_key" {
    null = false
    type = varchar(40)
  }
  column "session_data" {
    null = false
    type = longtext
  }
  column "expire_date" {
    null = false
    type = datetime(6)
  }
  primary_key {
    columns = [column.session_key]
  }
  index "django_session_expire_date_a5c62663" {
    columns = [column.expire_date]
  }
}
