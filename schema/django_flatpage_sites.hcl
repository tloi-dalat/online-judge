table "django_flatpage_sites" {
  schema = schema.online_judge
  column "id" {
    null           = false
    type           = int
    auto_increment = true
  }
  column "flatpage_id" {
    null = false
    type = int
  }
  column "site_id" {
    null = false
    type = int
  }
  primary_key {
    columns = [column.id]
  }
  foreign_key "django_flatpage_sites_flatpage_id_078bbc8b_fk_django_flatpage_id" {
    columns     = [column.flatpage_id]
    ref_columns = [table.django_flatpage.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  foreign_key "django_flatpage_sites_site_id_bfd8ea84_fk_django_site_id" {
    columns     = [column.site_id]
    ref_columns = [table.django_site.column.id]
    on_update   = RESTRICT
    on_delete   = RESTRICT
  }
  index "django_flatpage_sites_flatpage_id_site_id_0d29d9d1_uniq" {
    unique  = true
    columns = [column.flatpage_id, column.site_id]
  }
  index "django_flatpage_sites_site_id_bfd8ea84_fk_django_site_id" {
    columns = [column.site_id]
  }
}
