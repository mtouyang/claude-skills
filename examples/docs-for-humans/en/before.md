# Orders Database Backup and Restore

## Background

The **orders database** is a PostgreSQL 16 instance that holds **every customer order** since 2019. We take a **nightly logical backup** with `pg_dump` — historically we used filesystem snapshots, but those **silently produced corrupt copies** twice in 2023 when the volume was under heavy write load (see the incident notes), so **we moved to logical dumps**, which are slower but **verifiable**. Backups are written to `/backups/orders/` and are **kept for 14 days**; the retention job runs at 03:30 UTC and deletes anything older, which is why you **must not** store ad-hoc dumps in that directory if you want to keep them.

## Taking a manual backup

Before any schema migration you **must** take a manual backup. First check there is enough disk space with `df -h /backups` — a full dump is **about 40 GB** today (it was 12 GB in 2022, and the growth is why we added the check) and the job **will fail halfway** if the disk fills, leaving a **truncated file that looks valid**. Then run `pg_dump -Fc -d orders -f /backups/manual/orders-$(date +%F).dump` (we use the custom format `-Fc` because it lets `pg_restore` run **in parallel** and restore **single tables**, which plain SQL dumps cannot do). After it finishes you **must verify** the dump with `pg_restore --list /backups/manual/orders-$(date +%F).dump > /dev/null` — if this exits non-zero the dump is **unusable**.

## Restoring

Restoring is **dangerous**. **Never restore into production directly** — always restore into `orders_restore` first. Create it with `createdb orders_restore`, then run `pg_restore -j 4 -d orders_restore <dump file>` (4 jobs is what the staging host can handle; more jobs made it swap during the 2024 drill). **Stop the writer service** with `systemctl stop orders-writer` before swapping — the swap will fail if anything holds a connection (pooled clients in particular keep connections open for up to 10 minutes) — then swap the databases by renaming: `psql -c "ALTER DATABASE orders RENAME TO orders_old"` followed by `psql -c "ALTER DATABASE orders_restore RENAME TO orders"`. Finally **start the writer** again with `systemctl start orders-writer` and **check the row count** with `psql -d orders -c "SELECT count(*) FROM orders"` against the number in the backup log.

## Notes

Keep `orders_old` for **at least 24 hours** in case the restore was wrong. We chose renaming over dropping because a rename is **instant and reversible**, while re-restoring takes about 50 minutes.
