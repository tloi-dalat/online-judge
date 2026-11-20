table "judge_problem_tags" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "problem_id" {
    null = false
    type = int
  }
  column "organizationproblemtag_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_problem_tags_organizationproblemt_08c8fce1_fk_judge_org" {
    columns     = [column.organizationproblemtag_id]
    ref_columns = [table.judge_organizationproblemtag.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_problem_tags_problem_id_5bcb7e10_fk_judge_problem_id" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_problem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_problem_tags_organizationproblemt_08c8fce1_fk_judge_org" {
    columns = [column.organizationproblemtag_id]
  }
  index "judge_problem_tags_problem_id_organizationp_e0f2b9f7_uniq" {
    unique  = true
    columns = [column.problem_id, column.organizationproblemtag_id]
  }
}
