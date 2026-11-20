table "judge_commentlock" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "page" {
    null = false
    type = varchar(34)
  }
  primary_key {
    columns = [column.id]
  }
  index "judge_commentlock_page_3aec2c30" {
    columns = [column.page]
  }
}
