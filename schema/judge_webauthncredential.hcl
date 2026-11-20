table "judge_webauthncredential" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "name" {
    null = false
    type = varchar(100)
  }
  column "cred_id" {
    null = false
    type = varchar(255)
  }
  column "public_key" {
    null = false
    type = longtext
  }
  column "counter" {
    null = false
    type = bigint
  }
  column "user_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_webauthncredential_user_id_8eaad7d2_fk_judge_profile_id" {
    columns     = [column.user_id]
    ref_columns = [table.judge_profile.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "cred_id" {
    unique  = true
    columns = [column.cred_id]
  }
  index "judge_webauthncredential_user_id_8eaad7d2_fk_judge_profile_id" {
    columns = [column.user_id]
  }
}
