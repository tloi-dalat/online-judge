table "social_auth_code" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = bigint
    auto_increment = true
  }
  column "email" {
    null = false
    type = varchar(254)
  }
  column "code" {
    null = false
    type = varchar(32)
  }
  column "verified" {
    null = false
    type = bool
  }
  column "timestamp" {
    null = false
    type = datetime(6)
  }
  primary_key {
    columns = [column.id]
  }
  index "social_auth_code_code_a2393167" {
    columns = [column.code]
  }
  index "social_auth_code_email_code_801b2d02_uniq" {
    unique  = true
    columns = [column.email, column.code]
  }
  index "social_auth_code_timestamp_176b341f" {
    columns = [column.timestamp]
  }
}
