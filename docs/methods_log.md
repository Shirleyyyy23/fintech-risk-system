# 可复用方法日志（Methods Log）

> **重要**：这是本项目核心学习文件。每次用 AI / 跑通一个关键技术点，都用**自己的话**记一条。
> 格式：场景 + 做法 + 为什么 + 坑 + 复用场景。
> 目标：最高效率做完 + 90% 吸收。周末回看，凡"只是抄会没真懂"的，下周从零手写一遍。

---

## <关键技术点>  | YYYY-MM-DD
- **场景**：遇到什么问题 / 要实现什么
- **做法**：核心代码或 SQL（自己写过的，贴关键片段）
- **为什么**：为什么选它、和替代方案的取舍
- **坑**：踩过什么、怎么避
- **复用**：以后哪类任务直接套

---

### 模板示例（替换掉）
## 星型模型建表  | 2026-10-27
- **场景**：把信用/AML 数据落成数仓
- **做法**：`CREATE TABLE FACT_LOAN_APPLICATION (...)` + `DIM_*` 维度表，外键关联
- **为什么**：Kimball 维度建模；事实表不直接 JOIN，靠一致性维度（DIM_TIME / DIM_CUSTOMER）实现多源集成
- **坑**：不要在两张事实表间硬造 JOIN key（ID 不同源 = 造假）
- **复用**：任何"多源 + 多维分析"场景都套这套

---

### 方法：Windows 下 requirements.txt 中文注释导致 pip 安装报 GBK 解码错误  | 2026-10-27
- **场景**：`pip install -r requirements.txt` 在中文 Windows 上直接报 `UnicodeDecodeError: 'gbk' codec can't decode byte 0xa3`
- **做法**：把 `requirements.txt` 的注释改成**纯 ASCII（英文）**，删除所有中文字符，重跑安装命令即可。
- **为什么**：pip 在中文 Windows 默认用 GBK 读 requirements 文件；文件本身是 UTF-8 中文，字节对不上就炸。改 ASCII 是最稳的跨环境解法（装包命令里的 `-i 清华镜像` 不变）。
- **坑**：报错信息里的 `0xa3` 就是某个中文字符的字节；不是网络问题，别去折腾代理。
- **复用**：任何要在 Windows 跑的 `requirements.txt` / 脚本配置文件，注释一律用英文，避免再踩同款编码坑。

---

### 方法：数据库密码用环境变量，绝不写死进脚本  | 2026-10-27
- **场景**：Python 脚本要连 MySQL（或用 API key / token），密码放哪儿？
- **做法**：终端设 `$env:DB_PASSWORD="xxx"`（PowerShell，仅当前窗口有效；Git Bash 用 `export`）；脚本里 `os.environ["DB_PASSWORD"]` 读。连接代码统一放 `src/warehouse/db_utils.py` 的 `get_engine()`，别处 `from ... import get_engine`。
- **为什么**：① 密码不进代码 → 不会误 `git push` 泄漏（配合 `.gitignore`）；② 改密码/换环境只改终端，不动脚本；③ `get_engine()` 集中一处，连接参数改一次全局生效。
- **坑**：环境变量是"会话级"的——每次新开 PowerShell 都要重设一次；关掉窗口就清空（这反而是好事，不会持久化明文）。
- **复用**：任何要连库/用密钥的脚本都套这套；`db_utils.py` 还能 `python src/warehouse/db_utils.py` 直接测连通性（先确保 MySQL 跑着 + `fintech_risk` 库已建）。

---

### 方法：连接串（DSN）绝不手拼字符串，用驱动自带的 URL builder  | 2026-10-27
- **场景**：`create_engine(f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}")` 跑起来报
  `(2003, "Can't connect to MySQL server on '0124@127.0.0.1' ([Errno 11003] getaddrinfo failed)")`
- **做法**：改用 `sqlalchemy.engine.URL.create(drivername, username, password, host, port, database, query)`；
  跑之前先打印一份"我要连哪里"（user/host/port/db + 密码掩码长度），一次就能看出解析对不对。
- **为什么**：手拼字符串时，密码里的 `@`（还有 `:` `/` `#` `?`）会被当成 URL 分隔符。
  `@0124` 作为密码 → 第一个 `@` 被当作"账号信息结束"，主机名变成 `0124@127.0.0.1`，
  DNS 解析失败，报错伪装成网络问题。`URL.create()` 会对各字段做转义，从根上消除这类 bug。
- **坑**：报错文案里的 `getaddrinfo failed` / `Can't connect to MySQL server on` 极像网络或 MySQL 没启动，
  实际根因可能是密码格式。**排查顺序：先看解析出的 host 对不对，再看 1045（密码错）/ 1049（库不存在）/ 2003（连不上）**。
- **复用**：任何 DSN（MySQL/PostgreSQL/Redis/MongoDB/HTTP API URL）都用 URL builder；
  另：`1045 Access denied` = 账号密码错，`1049 Unknown database` = 库没建，`2003` = 服务没起或地址错，三种要分清。
