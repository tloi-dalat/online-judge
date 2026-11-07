table "judge_navigationbar" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "order" {
    null     = false
    type     = int
    unsigned = true
  }
  column "key" {
    null = false
    type = varchar(10)
  }
  column "label" {
    null = false
    type = varchar(20)
  }
  column "path" {
    null = false
    type = varchar(255)
  }
  column "regex" {
    null = false
    type = longtext
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
  column "parent_id" {
    null = true
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_navigationbar_parent_id_806f64e3_fk_judge_navigationbar_id" {
    columns     = [column.parent_id]
    ref_columns = [table.judge_navigationbar.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_navigationbar_order_48c84306" {
    columns = [column.order]
  }
  index "judge_navigationbar_parent_id_806f64e3" {
    columns = [column.parent_id]
  }
  index "judge_navigationbar_tree_id_e12b3b53" {
    columns = [column.tree_id]
  }
  index "key" {
    unique  = true
    columns = [column.key]
  }
  check "level" {
    expr = "`level` >= 0"
  }
  check "lft" {
    expr = "`lft` >= 0"
  }
  check "order" {
    expr = "`order` >= 0"
  }
  check "rght" {
    expr = "`rght` >= 0"
  }
  check "tree_id" {
    expr = "`tree_id` >= 0"
  }
}
