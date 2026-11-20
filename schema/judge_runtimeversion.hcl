table "judge_runtimeversion" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "name" {
    null = false
    type = varchar(64)
  }
  column "version" {
    null = false
    type = varchar(64)
  }
  column "priority" {
    null = false
    type = int
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
  foreign_key "judge_runtimeversion_judge_id_96482e9d_fk_judge_judge_id" {
    columns     = [column.judge_id]
    ref_columns = [table.judge_judge.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_runtimeversion_language_id_3ad8be59_fk_judge_language_id" {
    columns     = [column.language_id]
    ref_columns = [table.judge_language.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_runtimeversion_judge_id_96482e9d_fk_judge_judge_id" {
    columns = [column.judge_id]
  }
  index "judge_runtimeversion_language_id_3ad8be59_fk_judge_language_id" {
    columns = [column.language_id]
  }
}
