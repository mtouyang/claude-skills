# 訂單資料庫備份與還原

| 你的來意 | 去哪一節 | 要多久 |
|---|---|---|
| 準備做 schema 遷移 | [手動備份](#手動備份) | 20 分鐘 |
| 資料錯了，要拿回昨天的版本 | [還原](#還原) | 60 分鐘 |
| 確認昨晚的備份在不在 | `ls -lh /backups/orders/` | 1 分鐘 |

不確定要做哪一件，就先做最後一行。

## 手動備份

```bash
df -h /backups                                                         # 剩餘空間要大於備份大小（約 40 GB）
pg_dump -Fc -d orders -f /backups/manual/orders-$(date +%F).dump
pg_restore --list /backups/manual/orders-$(date +%F).dump > /dev/null  # 結束碼要是 0
```

1. 確認空間。完整備份約 40 GB。磁碟滿了，備份會做到一半停下，留下一個看起來正常的截斷檔。
2. 執行備份。用的是自訂格式，理由見 C2。
3. 驗證備份。**`pg_restore --list` 結束碼不是 0，這份備份就不能用，不要開始遷移。**

手動備份放 `/backups/manual/`，不要放 `/backups/orders/`。清理排程會刪掉 `/backups/orders/` 裡超過 14 天的檔。

## 還原

```bash
createdb orders_restore
pg_restore -j 4 -d orders_restore <備份檔>                             # 約 50 分鐘
systemctl stop orders-writer
psql -c "ALTER DATABASE orders RENAME TO orders_old"
psql -c "ALTER DATABASE orders_restore RENAME TO orders"
systemctl start orders-writer
psql -d orders -c "SELECT count(*) FROM orders"                        # 要等於備份紀錄裡的筆數
```

1. 還原到 `orders_restore`。**絕對不要直接還原到 `orders`。** 用 4 個 job，理由見 C3。
2. 停掉寫入服務。有任何連線沒放掉，改名就會失敗。連線池的客戶端最長會佔住連線 10 分鐘，改名被拒就等一下再試。
3. 用改名來切換兩個資料庫，理由見 C4。
4. 重新啟動寫入服務，拿筆數跟備份紀錄比。

`orders_old` 至少保留 24 小時，以防還原錯了。

## 附錄：為什麼是這個形狀

### C1. 這個資料庫

PostgreSQL 16，存放 2019 年以來的每一筆客戶訂單。每晚的邏輯備份寫到 `/backups/orders/`，保留 14 天。清理排程在 UTC 03:30 跑。

### C2. 邏輯備份與自訂格式

以前用檔案系統快照，但 2023 年在高寫入負載下兩次靜默產生損壞的副本（見事故紀錄）。邏輯備份比較慢，但可以驗證。自訂格式 `-Fc` 讓 `pg_restore` 可以平行還原，也能只還原單張表，純 SQL 備份做不到。

### C3. 還原用 4 個 job

這是 staging 主機扛得住的上限。2024 年演練時開更多就開始 swap。

### C4. 改名而不是刪庫

改名瞬間完成，而且可以撤回。重新還原要大約 50 分鐘。

### C5. 空間檢查

備份在 2022 年只有 12 GB，現在約 40 GB。就是因為長這麼快，才加了這個檢查。

---

## 這份動了什麼（轉正時拿掉）

- 規則一：加了分流表。第三行是原文沒處理的來意。
- 規則二：每個流程前面加一段完整指令串，註解寫要看到什麼。
- 規則三：粗體 23 → 2。留下的兩個是「備份不能用」和「不要直接還原到 `orders`」。
- 規則四：五段理由搬到 C1–C5。磁碟滿的警告和連線池要等的說明留在原地，因為它們會改變讀者當下的動作。
- 規則五：五處破折號插入句拆成獨立句子。
- 規則六：半形標點全部轉全形，`check_punct.py` 0 處。
- 沒有刪任何東西。行數 17 → 76。
