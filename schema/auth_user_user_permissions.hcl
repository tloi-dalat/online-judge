table "auth_user_user_permissions" {
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
  column "permission_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm" {
    columns     = [column.permission_id]
    ref_columns = [table.auth_permission.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id" {
    columns     = [column.user_id]
    ref_columns = [table.auth_user.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq" {
    unique  = true
    columns = [column.user_id, column.permission_id]
  }
  index "auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm" {
    columns = [column.permission_id]
  }
}
