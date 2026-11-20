table "judge_miscconfig" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "key" {
    null = false
    type = varchar(30)
  }
  column "value" {
    null = false
    type = longtext
  }
  primary_key {
    columns = [column.id]
  }
  index "judge_miscconfig_key_bb230360_uniq" {
    unique  = true
    columns = [column.key]
  }
}
