table "judge_commentvote" {
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
  column "comment_id" {
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
  foreign_key "judge_commentvote_comment_id_9711d946_fk_judge_comment_id" {
    columns     = [column.comment_id]
    ref_columns = [table.judge_comment.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_commentvote_voter_id_49326699_fk_judge_profile_id" {
    columns     = [column.voter_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_commentvote_comment_id_9711d946_fk_judge_comment_id" {
    columns = [column.comment_id]
  }
  index "judge_commentvote_voter_id_comment_id_2fa9cd9b_uniq" {
    unique  = true
    columns = [column.voter_id, column.comment_id]
  }
}
