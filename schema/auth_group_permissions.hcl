table "auth_group_permissions" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "group_id" {
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
  foreign_key "auth_group_permissio_permission_id_84c5c92e_fk_auth_perm" {
    columns     = [column.permission_id]
    ref_columns = [table.auth_permission.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "auth_group_permissions_group_id_b120cbf9_fk_auth_group_id" {
    columns     = [column.group_id]
    ref_columns = [table.auth_group.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" {
    unique  = true
    columns = [column.group_id, column.permission_id]
  }
  index "auth_group_permissio_permission_id_84c5c92e_fk_auth_perm" {
    columns = [column.permission_id]
  }
}
