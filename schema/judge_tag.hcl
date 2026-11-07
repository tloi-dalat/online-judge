table "judge_tag" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "code" {
    null = false
    type = varchar(30)
  }
  column "name" {
    null = false
    type = varchar(100)
  }
  column "group_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_tag_group_id_b1433d7f_fk_judge_taggroup_id" {
    columns     = [column.group_id]
    ref_columns = [table.judge_taggroup.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "code" {
    unique  = true
    columns = [column.code]
  }
  index "judge_tag_group_id_b1433d7f_fk_judge_taggroup_id" {
    columns = [column.group_id]
  }
  index "judge_tag_name_942c3a66" {
    columns = [column.name]
  }
}
