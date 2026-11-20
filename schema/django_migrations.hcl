table "django_migrations" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "app" {
    null = false
    type = varchar(255)
  }
  column "name" {
    null = false
    type = varchar(255)
  }
  column "applied" {
    null = false
    type = datetime(6)
  }
  primary_key {
    columns = [column.id]
  }
}
