table "judge_blogvote" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "score" {
    null = false
    type = int
  }
  column "blog_id" {
    null = false
    type = int
  }
  column "voter_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_blogvote_blog_id_9fe4f241_fk_judge_blogpost_id" {
    columns     = [column.blog_id]
    ref_columns = [table.judge_blogpost.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_blogvote_voter_id_49ace0bf_fk_judge_profile_id" {
    columns     = [column.voter_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_blogvote_blog_id_9fe4f241_fk_judge_blogpost_id" {
    columns = [column.blog_id]
  }
  index "judge_blogvote_voter_id_blog_id_ac6e59be_uniq" {
    unique  = true
    columns = [column.voter_id, column.blog_id]
  }
}
