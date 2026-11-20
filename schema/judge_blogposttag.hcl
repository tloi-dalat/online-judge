table "judge_blogposttag" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "name" {
    null = false
    type = varchar(40)
  }
  column "slug" {
    null = false
    type = varchar(50)
  }
  primary_key {
    columns = [column.id]
  }
  index "name" {
    unique  = true
    columns = [column.name]
  }
  index "slug" {
    unique  = true
    columns = [column.slug]
  }
}
