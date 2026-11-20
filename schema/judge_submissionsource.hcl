table "judge_submissionsource" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "source" {
    null = false
    type = longtext
  }
  column "submission_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_submissionsour_submission_id_d4abc888_fk_judge_sub" {
    columns     = [column.submission_id]
    ref_columns = [table.judge_submission.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "submission_id" {
    unique  = true
    columns = [column.submission_id]
  }
}
