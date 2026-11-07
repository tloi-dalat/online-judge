table "judge_submissiontestcase" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "case" {
    null = false
    type = int
  }
  column "status" {
    null = false
    type = varchar(3)
  }
  column "time" {
    null = true
    type = double
  }
  column "memory" {
    null = true
    type = double
  }
  column "points" {
    null = true
    type = double
  }
  column "total" {
    null = true
    type = double
  }
  column "batch" {
    null = true
    type = int
  }
  column "feedback" {
    null = false
    type = varchar(50)
  }
  column "extended_feedback" {
    null = false
    type = longtext
  }
  column "output" {
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
  foreign_key "judge_submissiontest_submission_id_a69f2d0e_fk_judge_sub" {
    columns     = [column.submission_id]
    ref_columns = [table.judge_submission.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_submissiontestcase_submission_id_case_7aba3b7b_uniq" {
    unique  = true
    columns = [column.submission_id, column.case]
  }
}
