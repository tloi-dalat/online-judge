table "registration_supervisedregistrationprofile" {
  schema = schema.online_judge
  column "registrationprofile_ptr_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.registrationprofile_ptr_id]
  }
  foreign_key "registration_supervi_registrationprofile__0a59f3b2_fk_registrat" {
    columns     = [column.registrationprofile_ptr_id]
    ref_columns = [table.registration_registrationprofile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
}
