table "judge_contest_tags" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "contest_id" {
    null = false
    type = int
  }
  column "contesttag_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_contest_tags_contest_id_998f99f7_fk_judge_contest_id" {
    columns     = [column.contest_id]
    ref_columns = [table.judge_contest.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "judge_contest_tags_contesttag_id_5d9788bd_fk_judge_contesttag_id" {
    columns     = [column.contesttag_id]
    ref_columns = [table.judge_contesttag.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_contest_tags_contesttag_id_5d9788bd_fk_judge_contesttag_id" {
    columns = [column.contesttag_id]
  }
  index "judge_contest_tags_contest_id_contesttag_id_eedb695b_uniq" {
    unique  = true
    columns = [column.contest_id, column.contesttag_id]
  }
}
