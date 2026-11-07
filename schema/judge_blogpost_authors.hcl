table "judge_blogpost_authors" {
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
  column "profile_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_blogpost_authors_blogpost_id_43745d7c_fk_judge_blogpost_id" {
    columns     = [column.blogpost_id]
    ref_columns = [table.judge_blogpost.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_blogpost_authors_profile_id_18d1d3e2_fk_judge_profile_id" {
    columns     = [column.profile_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_blogpost_authors_blogpost_id_profile_id_e53f2daf_uniq" {
    unique  = true
    columns = [column.blogpost_id, column.profile_id]
  }
  index "judge_blogpost_authors_profile_id_18d1d3e2_fk_judge_profile_id" {
    columns = [column.profile_id]
  }
}
