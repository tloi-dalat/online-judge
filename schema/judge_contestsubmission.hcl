table "judge_contestsubmission" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "points" {
    null = false
    type = double
  }
  column "is_pretest" {
    null = false
    type = bool
  }
  column "participation_id" {
    null = false
    type = int
  }
  column "problem_id" {
    null = false
    type = int
  }
  column "submission_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_contestsubmiss_participation_id_cf83bbb0_fk_judge_con" {
    columns     = [column.participation_id]
    ref_columns = [table.judge_contestparticipation.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_contestsubmiss_problem_id_1b1240d4_fk_judge_con" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_contestproblem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_contestsubmiss_submission_id_1384e5aa_fk_judge_sub" {
    columns     = [column.submission_id]
    ref_columns = [table.judge_submission.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_contestsubmiss_participation_id_cf83bbb0_fk_judge_con" {
    columns = [column.participation_id]
  }
  index "judge_contestsubmiss_problem_id_1b1240d4_fk_judge_con" {
    columns = [column.problem_id]
  }
  index "submission_id" {
    unique  = true
    columns = [column.submission_id]
  }
}
