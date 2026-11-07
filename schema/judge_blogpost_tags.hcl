table "judge_blogpost_tags" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "blogpost_id" {
    null = false
    type = int
  }
  column "blogposttag_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_blogpost_tags_blogpost_id_904851dc_fk_judge_blogpost_id" {
    columns     = [column.blogpost_id]
    ref_columns = [table.judge_blogpost.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_blogpost_tags_blogposttag_id_833a83c7_fk_judge_blo" {
    columns     = [column.blogposttag_id]
    ref_columns = [table.judge_blogposttag.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_blogpost_tags_blogposttag_id_833a83c7_fk_judge_blo" {
    columns = [column.blogposttag_id]
  }
  index "judge_blogpost_tags_blogpost_id_blogposttag_id_b1f415be_uniq" {
    unique  = true
    columns = [column.blogpost_id, column.blogposttag_id]
  }
}
