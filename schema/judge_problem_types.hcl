table "judge_problem_types" {
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
  column "problemtype_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_problem_types_problem_id_1c63e65f_fk_judge_problem_id" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_problem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_problem_types_problemtype_id_f51f1eea_fk_judge_pro" {
    columns     = [column.problemtype_id]
    ref_columns = [table.judge_problemtype.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_problem_types_problemtype_id_f51f1eea_fk_judge_pro" {
    columns = [column.problemtype_id]
  }
  index "judge_problem_types_problem_id_problemtype_id_db67c44c_uniq" {
    unique  = true
    columns = [column.problem_id, column.problemtype_id]
  }
}
