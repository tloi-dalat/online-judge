table "judge_contestannouncement" {
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
  column "description" {
    null = false
    type = longtext
  }
  column "date" {
    null = false
    type = datetime(6)
  }
  column "contest_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_contestannounc_contest_id_164cfbee_fk_judge_con" {
    columns     = [column.contest_id]
    ref_columns = [table.judge_contest.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_contestannounc_contest_id_164cfbee_fk_judge_con" {
    columns = [column.contest_id]
  }
}
