# 訂單資料庫備份與還原

## 背景

**訂單資料庫**是一台 PostgreSQL 16,存放 2019 年以來的**每一筆客戶訂單**.我們每晚用 `pg_dump` 做一次**邏輯備份**——以前用檔案系統快照,但 2023 年在高寫入負載下**兩次靜默產生損壞的副本**(見事故紀錄),所以**改成邏輯備份**,比較慢但**可以驗證**.備份寫到 `/backups/orders/`,**保留 14 天**;清理排程在 UTC 03:30 跑,會刪掉更舊的檔,所以想留的臨時備份**絕對不能**放在那個目錄.

## 手動備份

任何 schema 遷移之前**一定要**先做手動備份.先用 `df -h /backups` 確認空間夠——完整備份現在**約 40 GB**(2022 年只有 12 GB,就是因為長這麼快才加了這個檢查),磁碟滿了備份會**做到一半失敗**,留下一個**看起來正常的截斷檔**.然後執行 `pg_dump -Fc -d orders -f /backups/manual/orders-$(date +%F).dump`(用自訂格式 `-Fc` 是因為 `pg_restore` 可以**平行還原**、也能**只還原單張表**,純 SQL 備份做不到).做完**一定要驗證**:`pg_restore --list /backups/manual/orders-$(date +%F).dump > /dev/null`——結束碼不是 0 的話這份備份**不能用**.

## 還原

還原**很危險**.**絕對不要直接還原到正式庫**——一律先還原到 `orders_restore`.先 `createdb orders_restore`,再跑 `pg_restore -j 4 -d orders_restore <備份檔>`(4 個 job 是 staging 主機扛得住的上限,2024 年演練時開更多就開始 swap).切換前**停掉寫入服務**:`systemctl stop orders-writer`——有任何連線沒放掉,切換就會失敗(連線池的客戶端最長會佔住連線 10 分鐘)——然後用改名來切換:`psql -c "ALTER DATABASE orders RENAME TO orders_old"`,接著 `psql -c "ALTER DATABASE orders_restore RENAME TO orders"`.最後**重新啟動寫入服務** `systemctl start orders-writer`,並用 `psql -d orders -c "SELECT count(*) FROM orders"` **核對筆數**,跟備份紀錄裡的數字比.

## 備註

`orders_old` **至少保留 24 小時**,以防還原錯了.我們選改名而不是刪庫,是因為改名**瞬間完成而且可以撤回**,重新還原要大約 50 分鐘.
