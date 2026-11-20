table "judge_language" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "key" {
    null = false
    type = varchar(10)
  }
  column "name" {
    null = false
    type = varchar(20)
  }
  column "short_name" {
    null = true
    type = varchar(10)
  }
  column "common_name" {
    null = false
    type = varchar(20)
  }
  column "ace" {
    null = false
    type = varchar(20)
  }
  column "pygments" {
    null = false
    type = varchar(20)
  }
  column "template" {
    null = false
    type = longtext
  }
  column "info" {
    null = false
    type = varchar(50)
  }
  column "description" {
    null = false
    type = longtext
  }
  column "extension" {
    null = false
    type = varchar(10)
  }
  column "file_only" {
    null = false
    type = bool
  }
  column "file_size_limit" {
    null = false
    type = int
  }
  column "include_in_problem" {
    null = false
    type = bool
  }
  primary_key {
    columns = [column.id]
  }
  index "key" {
    unique  = true
    columns = [column.key]
  }
}
