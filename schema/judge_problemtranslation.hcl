table "judge_problemtranslation" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "language" {
    null = false
    type = varchar(7)
  }
  column "name" {
    null = false
    type = varchar(100)
  }
  column "description" {
    null = false
    type = longtext
  }
  column "problem_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_problemtranslation_problem_id_7acb27a7_fk_judge_problem_id" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_problem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_problemtranslation_name_3bfcdd8c" {
    columns = [column.name]
  }
  index "judge_problemtranslation_problem_id_language_ed6ab873_uniq" {
    unique  = true
    columns = [column.problem_id, column.language]
  }
}
