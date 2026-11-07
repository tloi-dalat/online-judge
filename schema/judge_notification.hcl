table "judge_notification" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "title" {
    null = false
    type = varchar(255)
  }
  column "body" {
    null = false
    type = longtext
  }
  column "url" {
    null = false
    type = varchar(255)
  }
  column "time" {
    null = false
    type = datetime(6)
  }
  column "read" {
    null = false
    type = bool
  }
  column "priority" {
    null = false
    type = int
  }
  column "recipient_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_notification_recipient_id_57de51da_fk_judge_profile_id" {
    columns     = [column.recipient_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_notif_recipie_9180e7_idx" {
    on {
      column = column.recipient_id
    }
    on {
      column = column.read
    }
    on {
      desc   = true
      column = column.priority
    }
    on {
      desc   = true
      column = column.time
    }
  }
}
