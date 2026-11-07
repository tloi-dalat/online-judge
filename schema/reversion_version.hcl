table "reversion_version" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "object_id" {
    null = false
    type = varchar(191)
  }
  column "format" {
    null = false
    type = varchar(255)
  }
  column "serialized_data" {
    null = false
    type = longtext
  }
  column "object_repr" {
    null = false
    type = longtext
  }
  column "content_type_id" {
    null = false
    type = int
  }
  column "revision_id" {
    null = false
    type = int
  }
  column "db" {
    null = false
    type = varchar(191)
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "reversion_version_content_type_id_7d0ff25c_fk_django_co" {
    columns     = [column.content_type_id]
    ref_columns = [table.django_content_type.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "reversion_version_revision_id_af9f6a9d_fk_reversion_revision_id" {
    columns     = [column.revision_id]
    ref_columns = [table.reversion_revision.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "reversion_version_db_content_type_id_objec_b2c54f65_uniq" {
    unique  = true
    columns = [column.db, column.content_type_id, column.object_id, column.revision_id]
  }
  index "reversion_version_revision_id_af9f6a9d_fk_reversion_revision_id" {
    columns = [column.revision_id]
  }
  index "reversion_v_content_f95daf_idx" {
    columns = [column.content_type_id, column.db]
  }
}
