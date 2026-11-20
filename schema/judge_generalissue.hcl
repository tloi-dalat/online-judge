table "judge_generalissue" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "issue_url" {
    null = false
    type = varchar(200)
  }
  primary_key {
    columns = [column.id]
  }
}
