table "judge_contesttag" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "name" {
    null = false
    type = varchar(50)
  }
  column "color" {
    null = false
    type = varchar(7)
  }
  column "description" {
    null = false
    type = longtext
  }
  primary_key {
    columns = [column.id]
  }
  index "name" {
    unique  = true
    columns = [column.name]
  }
}
