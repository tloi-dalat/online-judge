table "judge_judge_runtimes" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "judge_id" {
    null = false
    type = int
  }
  column "language_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_judge_runtimes_judge_id_770ad6a5_fk_judge_judge_id" {
    columns     = [column.judge_id]
    ref_columns = [table.judge_judge.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_judge_runtimes_language_id_9575fc7b_fk_judge_language_id" {
    columns     = [column.language_id]
    ref_columns = [table.judge_language.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_judge_runtimes_judge_id_language_id_ececbd6e_uniq" {
    unique  = true
    columns = [column.judge_id, column.language_id]
  }
  index "judge_judge_runtimes_language_id_9575fc7b_fk_judge_language_id" {
    columns = [column.language_id]
  }
}
