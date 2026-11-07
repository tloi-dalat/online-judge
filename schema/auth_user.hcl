table "auth_user" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "password" {
    null = false
    type = varchar(128)
  }
  column "last_login" {
    null = true
    type = datetime(6)
  }
  column "is_superuser" {
    null = false
    type = bool
  }
  column "username" {
    null = false
    type = varchar(150)
  }
  column "first_name" {
    null = false
    type = varchar(150)
  }
  column "last_name" {
    null = false
    type = varchar(150)
  }
  column "email" {
    null = false
    type = varchar(254)
  }
  column "is_staff" {
    null = false
    type = bool
  }
  column "is_active" {
    null = false
    type = bool
  }
  column "date_joined" {
    null = false
    type = datetime(6)
  }
  primary_key {
    columns = [column.id]
  }
  index "username" {
    unique  = true
    columns = [column.username]
  }
}
