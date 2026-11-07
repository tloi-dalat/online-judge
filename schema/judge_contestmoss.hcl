table "judge_contestmoss" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "language" {
    null = false
    type = varchar(10)
  }
  column "submission_count" {
    null     = false
    type     = int
    unsigned = true
  }
  column "url" {
    null = true
    type = varchar(200)
  }
  column "contest_id" {
    null = false
    type = int
  }
  column "problem_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_contestmoss_contest_id_24908198_fk_judge_contest_id" {
    columns     = [column.contest_id]
    ref_columns = [table.judge_contest.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_contestmoss_problem_id_5d8c1e4e_fk_judge_problem_id" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_problem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_contestmoss_contest_id_problem_id_language_52b59ba8_uniq" {
    unique  = true
    columns = [column.contest_id, column.problem_id, column.language]
  }
  index "judge_contestmoss_problem_id_5d8c1e4e_fk_judge_problem_id" {
    columns = [column.problem_id]
  }
  check "submission_count" {
    expr = "`submission_count` >= 0"
  }
}
