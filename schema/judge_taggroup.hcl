table "judge_taggroup" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "code" {
    null = false
    type = varchar(30)
  }
  column "name" {
    null = false
    type = varchar(100)
  }
  primary_key {
    columns = [column.id]
  }
  index "code" {
    unique  = true
    columns = [column.code]
  }
}
