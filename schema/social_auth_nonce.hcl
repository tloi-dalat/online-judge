table "social_auth_nonce" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = bigint
    auto_increment = true
  }
  column "server_url" {
    null = false
    type = varchar(255)
  }
  column "timestamp" {
    null = false
    type = int
  }
  column "salt" {
    null = false
    type = varchar(65)
  }
  primary_key {
    columns = [column.id]
  }
  index "social_auth_nonce_server_url_timestamp_salt_f6284463_uniq" {
    unique  = true
    columns = [column.server_url, column.timestamp, column.salt]
  }
  index "social_auth_nonce_timestamp_bc4d078a" {
    columns = [column.timestamp]
  }
}
