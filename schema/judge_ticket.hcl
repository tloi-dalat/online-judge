table "judge_ticket" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "title" {
    null = false
    type = varchar(100)
  }
  column "time" {
    null = false
    type = datetime(6)
  }
  column "notes" {
    null = false
    type = longtext
  }
  column "object_id" {
    null     = false
    type     = int
    unsigned = true
  }
  column "is_open" {
    null = false
    type = bool
  }
  column "content_type_id" {
    null = false
    type = int
  }
  column "user_id" {
    null = false
    type = int
  }
  column "is_contributive" {
    null = false
    type = bool
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_ticket_content_type_id_376ebcf9_fk_django_content_type_id" {
    columns     = [column.content_type_id]
    ref_columns = [table.django_content_type.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_ticket_user_id_5a5c0bce_fk_judge_profile_id" {
    columns     = [column.user_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_ticket_content_type_id_376ebcf9_fk_django_content_type_id" {
    columns = [column.content_type_id]
  }
  index "judge_ticket_user_id_5a5c0bce_fk_judge_profile_id" {
    columns = [column.user_id]
  }
  check "object_id" {
    expr = "`object_id` >= 0"
  }
}
