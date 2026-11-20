table "judge_ticket_assignees" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "ticket_id" {
    null = false
    type = int
  }
  column "profile_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_ticket_assignees_profile_id_84d298d8_fk_judge_profile_id" {
    columns     = [column.profile_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_ticket_assignees_ticket_id_0fd7b2f7_fk_judge_ticket_id" {
    columns     = [column.ticket_id]
    ref_columns = [table.judge_ticket.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_ticket_assignees_profile_id_84d298d8_fk_judge_profile_id" {
    columns = [column.profile_id]
  }
  index "judge_ticket_assignees_ticket_id_profile_id_6bdac784_uniq" {
    unique  = true
    columns = [column.ticket_id, column.profile_id]
  }
}
