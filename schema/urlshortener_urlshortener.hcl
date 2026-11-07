table "urlshortener_urlshortener" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = bigint
    auto_increment = true
  }
  column "original_url" {
    null = false
    type = varchar(200)
  }
  column "short_code" {
    null = false
    type = varchar(50)
  }
  column "created_time" {
    null = false
    type = datetime(6)
  }
  column "last_access_time" {
    null = true
    type = datetime(6)
  }
  column "access_count" {
    null     = false
    type     = int
    unsigned = true
  }
  column "is_active" {
    null = false
    type = bool
  }
  column "is_deactive" {
    null = false
    type = bool
  }
  primary_key {
    columns = [column.id]
  }
  index "short_code" {
    unique  = true
    columns = [column.short_code]
  }
}
