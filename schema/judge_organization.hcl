table "judge_organization" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "name" {
    null = false
    type = varchar(128)
  }
  column "slug" {
    null = false
    type = varchar(128)
  }
  column "short_name" {
    null = false
    type = varchar(20)
  }
  column "about" {
    null = false
    type = longtext
  }
  column "creation_date" {
    null = false
    type = datetime(6)
  }
  column "is_open" {
    null = false
    type = bool
  }
  column "slots" {
    null = true
    type = int
  }
  column "access_code" {
    null = true
    type = varchar(7)
  }
  column "logo_override_image" {
    null = false
    type = varchar(150)
  }
  column "performance_points" {
    null = false
    type = double
  }
  column "member_count" {
    null = false
    type = int
  }
  column "is_unlisted" {
    null = false
    type = bool
  }
  column "available_credit" {
    null = false
    type = double
  }
  column "current_consumed_credit" {
    null = false
    type = double
  }
  column "monthly_credit" {
    null = false
    type = double
  }
  column "monthly_free_credit_limit" {
    null = false
    type = double
  }
  column "notice" {
    null = false
    type = longtext
  }
  primary_key {
    columns = [column.id]
  }
  index "judge_organization_slug_5e7161c5_uniq" {
    unique  = true
    columns = [column.slug]
  }
}
