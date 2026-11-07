table "judge_tagproblem" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "code" {
    null = false
    type = varchar(32)
  }
  column "name" {
    null = false
    type = varchar(100)
  }
  column "link" {
    null = false
    type = varchar(200)
  }
  column "judge" {
    null = true
    type = varchar(30)
  }
  primary_key {
    columns = [column.id]
  }
  index "code" {
    unique  = true
    columns = [column.code]
  }
  index "judge_tagproblem_judge_f9d2c6b5" {
    columns = [column.judge]
  }
  index "judge_tagproblem_name_a8e1541e" {
    columns = [column.name]
  }
}
