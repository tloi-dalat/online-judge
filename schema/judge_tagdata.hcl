table "judge_tagdata" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "assigner_id" {
    null = false
    type = int
  }
  column "problem_id" {
    null = false
    type = int
  }
  column "tag_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_tagdata_assigner_id_e3c18347_fk_judge_profile_id" {
    columns     = [column.assigner_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_tagdata_problem_id_58e0fe06_fk_judge_tagproblem_id" {
    columns     = [column.problem_id]
    ref_columns = [table.judge_tagproblem.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_tagdata_tag_id_ae307bf9_fk_judge_tag_id" {
    columns     = [column.tag_id]
    ref_columns = [table.judge_tag.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_tagdata_assigner_id_e3c18347_fk_judge_profile_id" {
    columns = [column.assigner_id]
  }
  index "judge_tagdata_problem_id_58e0fe06_fk_judge_tagproblem_id" {
    columns = [column.problem_id]
  }
  index "judge_tagdata_tag_id_problem_id_8bea076a_uniq" {
    unique  = true
    columns = [column.tag_id, column.problem_id]
  }
}
