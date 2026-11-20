table "social_auth_association" {
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
  column "handle" {
    null = false
    type = varchar(255)
  }
  column "secret" {
    null = false
    type = varchar(255)
  }
  column "issued" {
    null = false
    type = int
  }
  column "lifetime" {
    null = false
    type = int
  }
  column "assoc_type" {
    null = false
    type = varchar(64)
  }
  primary_key {
    columns = [column.id]
  }
  index "social_auth_association_server_url_handle_078befa2_uniq" {
    unique  = true
    columns = [column.server_url, column.handle]
  }
}
