table "judge_problemgroup" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "name" {
    null = false
    type = varchar(20)
  }
  column "full_name" {
    null = false
    type = varchar(100)
  }
  primary_key {
    columns = [column.id]
  }
  index "name" {
    unique  = true
    columns = [column.name]
  }
}
