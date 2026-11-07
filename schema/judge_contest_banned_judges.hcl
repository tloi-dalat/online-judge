table "judge_contest_banned_judges" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "contest_id" {
    null = false
    type = int
  }
  column "judge_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_contest_banned_contest_id_9dda648c_fk_judge_con" {
    columns     = [column.contest_id]
    ref_columns = [table.judge_contest.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_contest_banned_judges_judge_id_27dd8be2_fk_judge_judge_id" {
    columns     = [column.judge_id]
    ref_columns = [table.judge_judge.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_contest_banned_judges_contest_id_judge_id_25704a78_uniq" {
    unique  = true
    columns = [column.contest_id, column.judge_id]
  }
  index "judge_contest_banned_judges_judge_id_27dd8be2_fk_judge_judge_id" {
    columns = [column.judge_id]
  }
}
