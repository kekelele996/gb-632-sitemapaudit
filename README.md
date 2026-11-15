# sitemapaudit 政务公开目录与 sitemap 收录对账

河州市政务公开办网站编辑部每季度要核对 3 个政务站的公开目录与 sitemap 收录：
目录页写了什么、sitemap 收录了什么、这些地址还能不能打开。现状是打开三个站
逐条肉眼比对，2.4 万条目录对不完。本项目把这段流程做成一次可复算的巡检。

## 能力

- 采信：三站目录页 + `sitemap.xml`，编码回退链、BOM 剥离、块级严格校验、行号保真
- 规范化：7 步固定顺序得到比较键，改写痕迹逐条留证
- 可达性：逐跳探测（不自动跟随），状态码 0/4xx/5xx 分开记，跳转上限 5 跳
- 三向对账：目录 / 收录 / 可达 三集合，7 类缺陷 + 对平，四账守恒
- 缺陷单：按分类筛选，CSV（含原始写法）与运行清单 JSON 导出，可打印
- 批次：批次键幂等重跑、阶段可单独跑、可续跑

## 模块

| 模块 | 动作 | 入口 |
|---|---|---|
| M1 目录采信 | 取目录页与 sitemap，逐行留行号，坏块进隔离区 | `POST /api/crawl` |
| M2 URL 规则 | 契约查询、地址规范化试算 | `GET /api/contract` `POST /api/url/normalize` |
| M3 可达性 | 逐地址状态码、跳转链、分类 | `GET /api/reachability` |
| M4 三向对账 | 四账、交叉表、分类合计 | `GET /api/reconcile` |
| M5 巡检批次 | 批次历史、停止点、续跑 | `GET /api/batches` `POST /api/batches/{run_id}/resume` |
| M6 缺陷单 | 缺陷筛选、CSV、运行清单 | `GET /api/defects` `GET /api/defects.csv` `GET /api/export/manifest.json` |

页面：`/` 巡检运行、`/sites` 站点与目录、`/reach` 可达性明细、`/reconcile` 对账缺陷、
`/batches` 批次历史、`/defects` 缺陷单。

## 核心规则

1. 规范化 7 步（scheme → host → relative → path → tracking → query → fragment），
   比较键 = 规范化后的完整地址；规则表见 `docs/DATA-DICTIONARY.md`。
2. 分类互斥，优先级固定：死链 > 跳转 > 重复条目 > 漏收录 > 目录未登记 > 地址不规范 > 对平。
   规则表带优先级排序后判定，书写顺序不影响结论。
3. 四账：目录 / 收录 / 可达 / 缺陷四个等式必须成立，否则整批记 `failed`。

## 规则与已知不覆盖

- 数值与时间规则、空态三态、批次键定义见 `docs/DATA-DICTIONARY.md`。
- 陷阱登记与不覆盖项见 `docs/DEPTH.md`（含 10 条 TRAP 与对应测试）。
- 已知不覆盖：`sitemapindex` 索引、正文内容比对、并发探测。

## 启动

```bash
docker compose up -d --build          # 主服务 18201，样例站 19201
curl -s localhost:18201/healthz
curl -s -X POST localhost:18201/api/crawl -H 'content-type: application/json' -d '{}'
```

本地不装容器时：

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
SAMPLE_SITE_BASE=http://127.0.0.1:19201 python3 -m http.server 19201 --directory sample_site &
SAMPLE_SITE_BASE=http://127.0.0.1:19201 SITEMAPAUDIT_DB=/tmp/audit.sqlite \
  uvicorn app.main:create_app --factory --port 18201
```

重建数据库：删除 `audit-data` 卷（`docker compose down -v`）后重新启动。

## 演示步骤

1. 打开 `http://localhost:18201/`，点「触发巡检」，看三阶段账与原因码分布。
2. `/sites` 看目录条目：`site-b` 的编码是 `gb18030`，`site-a` 有旧属性与冲突行。
3. `/reach` 按分类过滤，点开 `跳转链` 能看到两跳的旧路径。
4. `/reconcile` 看四账与三向交叉表；`/defects` 导出 CSV 与运行清单并打印。

## 测试

```bash
pytest -q          # 67 个测试函数 / 69 个用例
python3 ~/.dsh/skills/pr-batch-simple/scripts/check_project.py . --scale medium
```

## 目录

```
app/                     平台层 + 六个功能模块
app/templates/           7 个页面（base + 6）
app/static/              theme.css layout.css components.css + 3 个脚本
docs/                    DEPTH.md DATA-DICTIONARY.md
sample_site/             三站目录页 + sitemap + serve.py（样例站服务）
sample_data/degenerate/  空态与截断样例
tests/                   每模块一组 + e2e + fixtures
```
