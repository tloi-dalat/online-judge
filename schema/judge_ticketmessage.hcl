table "judge_ticketmessage" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "body" {
    null = false
    type = longtext
  }
  column "time" {
    null = false
    type = datetime(6)
  }
  column "ticket_id" {
    null = false
    type = int
  }
  column "user_id" {
    null = false
    type = int
  }
  column "action" {
    null = false
    type = varchar(10)
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_ticketmessage_ticket_id_5e413158_fk_judge_ticket_id" {
    columns     = [column.ticket_id]
    ref_columns = [table.judge_ticket.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_ticketmessage_user_id_1dbfbfb0_fk_judge_profile_id" {
    columns     = [column.user_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_ticketmessage_ticket_id_5e413158_fk_judge_ticket_id" {
    columns = [column.ticket_id]
  }
  index "judge_ticketmessage_user_id_1dbfbfb0_fk_judge_profile_id" {
    columns = [column.user_id]
  }
}
