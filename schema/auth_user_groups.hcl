table "auth_user_groups" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "user_id" {
    null = false
    type = int
  }
  column "group_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "auth_user_groups_group_id_97559544_fk_auth_group_id" {
    columns     = [column.group_id]
    ref_columns = [table.auth_group.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "auth_user_groups_user_id_6a12ed8b_fk_auth_user_id" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "auth_user_groups_group_id_97559544_fk_auth_group_id" {
    columns = [column.group_id]
  }
  index "auth_user_groups_user_id_group_id_94350c0c_uniq" {
    unique  = true
    columns = [column.user_id, column.group_id]
  }
}
