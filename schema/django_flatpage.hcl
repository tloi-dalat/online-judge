table "django_flatpage" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "url" {
    null = false
    type = varchar(100)
  }
  column "title" {
    null = false
    type = varchar(200)
  }
  column "content" {
    null = false
    type = longtext
  }
  column "enable_comments" {
    null = false
    type = bool
  }
  column "template_name" {
    null = false
    type = varchar(70)
  }
  column "registration_required" {
    null = false
    type = bool
  }
  primary_key {
    columns = [column.id]
  }
  index "django_flatpage_url_41612362" {
    columns = [column.url]
  }
}
