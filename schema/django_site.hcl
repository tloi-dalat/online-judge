table "django_site" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "domain" {
    null = false
    type = varchar(100)
  }
  column "name" {
    null = false
    type = varchar(50)
  }
  primary_key {
    columns = [column.id]
  }
  index "django_site_domain_a2e37b91_uniq" {
    unique  = true
    columns = [column.domain]
  }
}
