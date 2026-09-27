# Orders Database Backup and Restore

| Why you are here | Go to | Time |
|---|---|---|
| About to run a schema migration | [Take a manual backup](#take-a-manual-backup) | 20 min |
| Data is wrong and you need yesterday's copy | [Restore](#restore) | 60 min |
| Checking whether last night's backup exists | `ls -lh /backups/orders/` | 1 min |

Not sure which one you need? Start with the last row.

## Take a manual backup

```bash
df -h /backups                                                         # expect more free space than the dump (about 40 GB)
pg_dump -Fc -d orders -f /backups/manual/orders-$(date +%F).dump
pg_restore --list /backups/manual/orders-$(date +%F).dump > /dev/null  # expect exit code 0
```

1. Check free space. A full dump is about 40 GB. If the disk fills, the dump stops halfway and leaves a truncated file that looks valid.
2. Run the dump. It uses the custom format. Reason: see C2.
3. Verify the dump. **If `pg_restore --list` exits non-zero, the dump is unusable. Do not start the migration.**

Write manual dumps to `/backups/manual/`, not `/backups/orders/`. The retention job deletes anything in `/backups/orders/` older than 14 days.

## Restore

```bash
createdb orders_restore
pg_restore -j 4 -d orders_restore <dump file>                         # about 50 min
systemctl stop orders-writer
psql -c "ALTER DATABASE orders RENAME TO orders_old"
psql -c "ALTER DATABASE orders_restore RENAME TO orders"
systemctl start orders-writer
psql -d orders -c "SELECT count(*) FROM orders"                        # expect the count in the backup log
```

1. Restore into `orders_restore`. **Never restore into `orders` directly.** Use 4 jobs. Reason: see C3.
2. Stop the writer service. The rename fails if anything still holds a connection. Pooled clients keep connections open for up to 10 minutes, so wait if the rename is refused.
3. Swap the databases by renaming them. Reason: see C4.
4. Start the writer and compare the row count with the backup log.

Keep `orders_old` for at least 24 hours in case the restore was wrong.

## Appendix: why it is this way

### C1. The database.

PostgreSQL 16, every customer order since 2019. Nightly logical backups go to `/backups/orders/` and are kept for 14 days. The retention job runs at 03:30 UTC.

### C2. Logical dumps in custom format.

Filesystem snapshots silently produced corrupt copies twice in 2023 under heavy write load (see the incident notes). Logical dumps are slower but can be verified. The custom format `-Fc` lets `pg_restore` run in parallel and restore single tables, which plain SQL dumps cannot.

### C3. Four restore jobs.

That is what the staging host can handle. More jobs made it swap during the 2024 drill.

### C4. Rename instead of drop.

A rename is instant and reversible. Re-restoring takes about 50 minutes.

### C5. The disk space check.

The dump was 12 GB in 2022 and is about 40 GB now. The check was added because of that growth.

---

## Change summary (remove when finalising)

- Rule 1: added the routing table. The third row covers a reason the original never addressed.
- Rule 2: added one command block per procedure, with expected output in comments.
- Rule 3: bold 23 → 2. The two left are "the dump is unusable" and "never restore into `orders` directly".
- Rule 4: moved five reasons to C1–C5. Kept the full-disk warning and the pooled-client wait in place, because they change what the reader does.
- Rule 5: split five em-dash asides into separate sentences.
- Nothing deleted. Lines 17 → 75.
