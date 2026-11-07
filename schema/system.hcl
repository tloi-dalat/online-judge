table "schema_migrations" {
  schema = schema.online_judge
  column "version" {
    null = false
    type = bigint
  }
  column "dirty" {
    null = false
    type = bool
  }
  primary_key {
    columns = [column.version]
  }
}
