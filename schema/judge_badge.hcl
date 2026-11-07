table "judge_badge" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "name" {
    null = false
    type = varchar(128)
  }
  column "mini" {
    null = false
    type = varchar(200)
  }
  column "full_size" {
    null = false
    type = varchar(200)
  }
  primary_key {
    columns = [column.id]
  }
}
