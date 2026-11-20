table "judge_comment" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "time" {
    null = false
    type = datetime(6)
  }
  column "page" {
    null = false
    type = varchar(34)
  }
  column "score" {
    null = false
    type = int
  }
  column "body" {
    null = false
    type = longtext
  }
  column "hidden" {
    null = false
    type = bool
  }
  column "lft" {
    null     = false
    type     = int
    unsigned = true
  }
  column "rght" {
    null     = false
    type     = int
    unsigned = true
  }
  column "tree_id" {
    null     = false
    type     = int
    unsigned = true
  }
  column "level" {
    null     = false
    type     = int
    unsigned = true
  }
  column "author_id" {
    null = false
    type = int
  }
  column "parent_id" {
    null = true
    type = int
  }
  column "revisions" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_comment_author_id_ec3f8371_fk_judge_profile_id" {
    columns     = [column.author_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_comment_parent_id_e16fe797_fk_judge_comment_id" {
    columns     = [column.parent_id]
    ref_columns = [table.judge_comment.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_comment_author_id_ec3f8371_fk_judge_profile_id" {
    columns = [column.author_id]
  }
  index "judge_comment_page_66eb6c11" {
    columns = [column.page]
  }
  index "judge_comment_parent_id_e16fe797" {
    columns = [column.parent_id]
  }
  index "judge_comment_tree_id_cdde24bd" {
    columns = [column.tree_id]
  }
  check "level" {
    expr = "`level` >= 0"
  }
  check "lft" {
    expr = "`lft` >= 0"
  }
  check "rght" {
    expr = "`rght` >= 0"
  }
  check "tree_id" {
    expr = "`tree_id` >= 0"
  }
}
