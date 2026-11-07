table "judge_blogpost" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "title" {
    null = false
    type = varchar(100)
  }
  column "slug" {
    null = false
    type = varchar(50)
  }
  column "visible" {
    null = false
    type = bool
  }
  column "sticky" {
    null = false
    type = bool
  }
  column "publish_on" {
    null = false
    type = datetime(6)
  }
  column "content" {
    null = false
    type = longtext
  }
  column "summary" {
    null = false
    type = longtext
  }
  column "og_image" {
    null = false
    type = varchar(150)
  }
  column "global_post" {
    null = false
    type = bool
  }
  column "organization_id" {
    null = true
    type = int
  }
  column "score" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "judge_blogpost_organization_id_d1eb4e89_fk_judge_organization_id" {
    columns     = [column.organization_id]
    ref_columns = [table.judge_organization.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "judge_blogpost_organization_id_d1eb4e89_fk_judge_organization_id" {
    columns = [column.organization_id]
  }
  index "judge_blogpost_slug_eb303bae" {
    columns = [column.slug]
  }
}
