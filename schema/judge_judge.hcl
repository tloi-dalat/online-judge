table "judge_judge" {
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
  column "created" {
    null = false
    type = datetime(6)
  }
  column "auth_key" {
    null = false
    type = varchar(100)
  }
  column "is_blocked" {
    null = false
    type = bool
  }
  column "online" {
    null = false
    type = bool
  }
  column "start_time" {
    null = true
    type = datetime(6)
  }
  column "ping" {
    null = true
    type = double
  }
  column "load" {
    null = true
    type = double
  }
  column "description" {
    null = false
    type = longtext
  }
  column "last_ip" {
    null = true
    type = char(39)
  }
  column "is_disabled" {
    null = false
    type = bool
  }
  column "tier" {
    null     = false
    type     = int
    unsigned = true
  }
  column "storages" {
    null = false
    type = json
  }
  primary_key {
    columns = [column.id]
  }
  index "name" {
    unique  = true
    columns = [column.name]
  }
  check "tier" {
    expr = "`tier` >= 0"
  }
}
