table "judge_contestproblem" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "points" {
    null = false
    type = int
  }
  column "partial" {
    null = false
    type = bool
  }
  column "is_pretested" {
    null = false
    type = bool
  }
  column "order" {
    null     = false
    type     = int
    unsigned = true
  }
  column "output_prefix_override" {
    null = true
    type = int
  }
  column "max_submissions" {
    null = true
    type = int
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
  foreign_key "judge_contestproblem_contest_id_b28b7107_fk_judge_contest_id" {
    columns     = [column.contest_id]
    ref_columns = [table.judge_contest.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_contestproblem_problem_id_fc63c700_fk_judge_problem_id" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_problem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_contestproblem_contest_id_b28b7107_fk_judge_contest_id" {
    columns = [column.contest_id]
  }
  index "judge_contestproblem_order_05ce0638" {
    columns = [column.order]
  }
  index "judge_contestproblem_problem_id_contest_id_4ae77fe0_uniq" {
    unique  = true
    columns = [column.problem_id, column.contest_id]
  }
  check "order" {
    expr = "`order` >= 0"
  }
}
