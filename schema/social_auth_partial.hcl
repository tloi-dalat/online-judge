table "social_auth_partial" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = bigint
    auto_increment = true
  }
  column "token" {
    null = false
    type = varchar(32)
  }
  column "next_step" {
    null     = false
    type     = smallint
    unsigned = true
  }
  column "backend" {
    null = false
    type = varchar(32)
  }
  column "timestamp" {
    null = false
    type = datetime(6)
  }
  column "data" {
    null = false
    type = json
  }
  primary_key {
    columns = [column.id]
  }
  index "social_auth_partial_timestamp_50f2119f" {
    columns = [column.timestamp]
  }
  index "social_auth_partial_token_3017fea3" {
    columns = [column.token]
  }
  check "next_step" {
    expr = "`next_step` >= 0"
  }
}
