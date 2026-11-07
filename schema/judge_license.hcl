table "judge_license" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "key" {
    null = false
    type = varchar(20)
  }
  column "link" {
    null = false
    type = varchar(256)
  }
  column "name" {
    null = false
    type = varchar(256)
  }
  column "display" {
    null = false
    type = varchar(256)
  }
  column "icon" {
    null = false
    type = varchar(256)
  }
  column "text" {
    null = false
    type = longtext
  }
  primary_key {
    columns = [column.id]
  }
  index "key" {
    unique  = true
    columns = [column.key]
  }
}
