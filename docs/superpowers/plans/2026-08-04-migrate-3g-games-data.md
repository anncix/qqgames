# 3g_games 数据迁移到 qqgames 合并重构计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 以 qqgames 为主体，将 3g_games 的 8 款游戏数据迁移合并进来，引入多货币钱包，最终得到一台可运行的、数据更丰富的 QQ 家园平台。

**Architecture:** 保留 qqgames 的同步 SQLAlchemy + JWT + 多货币钱包骨架；在其 6 款游戏基础上迁入 3g_games 的丰富种子数据（spec 驱动），并新增风云三国、幻想西游 2 款游戏模块。数据迁移以「程序化种子生成器」形式移植，而非一次性 SQL 导入，保证幂等与可扩展。

**Tech Stack:** FastAPI、SQLAlchemy (sync)、Jinja2、bcrypt、python-jose、SQLite

---

## 背景与现状

### qqgames（主体，待改造）
- 克隆位置：`/Users/mubai/3g_games/qqgames`
- 同步 SQLAlchemy，`sqlite:///./qqhome.db`
- JWT 认证（`utils/auth.py`）
- **多货币钱包**：`Wallet` 表（g_coin / gold_coin / premium_coin）+ `WalletLog` 流水
- 6 款游戏：jingwutang(精武堂) / magic_garden(魔法花园) / sunny_farm(阳光牧场) / delicious_town(美味小镇) / zongheng_sihai(纵横四海) / summon_king(召唤之王)
- 种子数据：`main.py init_default_data()` 静态列表 + `utils/jingwutang.py init_jingwu_data()`
- 模块：`routers/`, `models/models.py`(70 表), `templates/`, `utils/`

### 3g_games（数据源）
- 位置：`/Users/mubai/3g_games/app`
- 异步 SQLAlchemy + aiosqlite，session 认证
- 单货币（coins）
- 8 款游戏：farm(农场) / town(小镇) / garden(花园) / sea(四海) / summon(召唤) / martial(精武) / fengyun(风云) / xyou(西游)
- 种子数据：程序化生成器 `app/seed_*.py`（spec 驱动，幂等，数据量巨大）
  - seed_garden_large.py: 520 作物 / 1024 材料 / 1536 配方 / 3072 订单
  - seed_sea_large.py: 20 城市 / 24 套装 / 60 宝石 / 21 卡片 / 40 圣痕 / 60 宠物 / 12 坐骑 / 8 羽翼 / 9 随从 / 10 副本
  - seed_farm_large.py: 49 作物
  - seed_town_large.py: 217 食材
  - seed_sea_v018.py: 14 船 / 12 主线 / 23 技能 / 34 特产 / 16 城市
  - seed_sea_equips.py: 79 装备
  - seed_fengyun.py: 13 城市 / 30 技能 / 105 装备 / 48 系列 / 11 名器 / 14 BOSS / 13 副本 / 15 称号 / 21 成就 / 189 物品
  - seed_xyou.py: 10 场景 / 45 技能 / 108 装备 / 8 龙宫叉 / 22 副本 / 13 宠物 / 116 物品 / 14 药品 / 19 高级材料 / 12 坐标

### 游戏映射
| qqgames 模块 | 3g_games 模块 | 数据源 |
|---|---|---|
| jingwutang | martial | seed_*（martial 数据在程序内不复用 seed）|
| magic_garden | garden | seed_garden_large.py |
| sunny_farm | farm | seed_farm_large.py |
| delicious_town | town | seed_town_large.py |
| zongheng_sihai | sea | seed_sea_large.py + seed_sea_v018.py + seed_sea_equips.py |
| summon_king | summon | 程序内静态数据 |
| **（新增）fengyun** | fengyun | seed_fengyun.py |
| **（新增）xyou** | xyou | seed_xyou.py |

---

## 迁移决策（修订版）

> 关键核查结论：3g_games 的 `seed_*.py` 是**异步生成器 + 强绑定专属模型**（GardenBloom/FengyunCity/XyouScene 等），qqgames 无这些模型，无法直接移植。但 `routers/*_data.py` 是**纯静态常量**（无模型依赖），可完整迁移。

1. **主体保留 qqgames 架构**：同步 SQLAlchemy、JWT、模板、多货币钱包不动。
2. **数据迁移形式**：迁移 3g_games 的**纯静态数据常量**（`routers/*_data.py`），为 qqgames 新建对应模型 + 同步种子生成器 + 路由 + 模板，挂到 qqgames 的 `main.py init_default_data()` 之后，保证幂等。
3. **多货币接入**：qqgames 已有 `Wallet`。将 3g_games 各模块的「金币/银两」按模块映射到 Wallet 货币字段（g_coin 为主，sea 用 silver_coin 语义映射到 g_coin 或新增字段），并通过 `utils/common.py change_currency()` 统一记账。
4. **新增 2 款游戏**：fengyun、xyou 需在 qqgames 新建 models + routers + templates + 同步种子生成器，复用 qqgames 的同步 Session 与 JWT 认证。
5. **数据量完整保留**：520 作物/1024 材料/1536 配方/3072 订单等全量迁移，不裁剪。
6. **共享 6 款改造**：garden/farm/town/sea 需在 qqgames 新建或扩展模型以承载 3g_games 丰富数据；jingwutang/summon 补充缺失数据。

---

## 任务分解

### Task 1: 建立迁移环境与基线验证
**Files:**
- Modify: `requirements.txt`
- Test: `tests/test_baseline.py`

- [ ] **Step 1: 确认依赖齐备**
  - `requirements.txt` 已含 fastapi/sqlalchemy/jinja2/bcrypt/python-jose。
  - 补充 `pytest`、`httpx` 到 requirements（用于测试）。

- [ ] **Step 2: 写基线导入测试**
```python
# tests/test_baseline.py
from starlette.testclient import TestClient
from main import app

def test_baseline_imports():
    client = TestClient(app)
    assert client.get("/auth/login").status_code == 200
```

- [ ] **Step 3: 运行测试确认基线通过**
```bash
cd /Users/mubai/3g_games/qqgames && source .venv/bin/activate && python -m pytest tests/test_baseline.py -v
```
Expected: PASS

- [ ] **Step 4: Commit**
```bash
git add -A && git commit -m "chore: 迁移环境基线 + 测试依赖"
```

### Task 2: 移植多货币钱包工具（若缺失）
**Files:**
- Modify: `utils/common.py`

- [ ] **Step 1: 确认 `utils/common.py` 已有 `change_currency`**
  读取 `utils/common.py`，若无则补：
```python
def change_currency(db, user_id, currency, amount, source_type="", source_id=None, remark=""):
    """多货币记账：currency ∈ {g_coin, gold_coin, premium_coin}"""
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise ValueError("wallet not found")
    before = getattr(wallet, currency)
    setattr(wallet, currency, before + amount)
    db.add(WalletLog(user_id=user_id, currency_type=currency, change_amount=amount,
                     before_amount=before, after_amount=before + amount,
                     source_type=source_type, source_id=source_id, remark=remark))
    db.commit()
    return before + amount
```

- [ ] **Step 2: 验证 `Wallet` 模型存在**（models.py 已有）

- [ ] **Step 3: Commit**

### Task 3: 移植魔法花园数据（garden）
**Files:**
- Create: `seed/seed_garden_large.py`
- Modify: `main.py`

- [ ] **Step 1: 移植生成器**（从 3g_games seed_garden_large.py 转同步版）
  核心：GardenFlower / GardenSeed / GardenAlbumEntry / GardenRecipe / GardenOrderTemplate，幂等写入。

- [ ] **Step 2: 挂到 main.py init_default_data 之后**

- [ ] **Step 3: 运行验证数据量**
```bash
python -c "from models.database import SessionLocal; from models.models import GardenFlower; db=SessionLocal(); print(db.query(GardenFlower).count())"
```

- [ ] **Step 4: Commit**

### Task 4: 移植纵横四海数据（sea）
**Files:**
- Create: `seed/seed_sea_large.py`, `seed/seed_sea_v018.py`, `seed/seed_sea_equips.py`
- Modify: `main.py`

- [ ] **Step 1: 移植 3 个生成器**（城市/套装/宝石/卡片/圣痕/宠物/坐骑/羽翼/随从/副本/船/主线/技能/特产/装备）
- [ ] **Step 2: 挂到 main.py**
- [ ] **Step 3: 验证城市/装备数量**
- [ ] **Step 4: Commit**

### Task 5: 移植农场数据（farm）
**Files:**
- Create: `seed/seed_farm_large.py`
- Modify: `main.py`

- [ ] **Step 1: 移植 49 作物生成器**
- [ ] **Step 2: 挂载 + 验证 + Commit**

### Task 6: 移植小镇数据（town）
**Files:**
- Create: `seed/seed_town_large.py`
- Modify: `main.py`

- [ ] **Step 1: 移植 217 食材生成器**
- [ ] **Step 2: 挂载 + 验证 + Commit**

### Task 7: 移植精武堂数据（martial → jingwutang）
**Files:**
- Modify: `utils/jingwutang.py`

- [ ] **Step 1: 对比 3g_games martial_* 数据，补充 qqgames jingwutang 静态数据缺失项**
- [ ] **Step 2: 验证 + Commit**

### Task 8: 移植召唤之王数据（summon）
**Files:**
- Modify: `routers/summon_king.py` / `utils/`

- [ ] **Step 1: 对比 summon_data.py，补充 qqgames summon 幻兽/技能数据**
- [ ] **Step 2: 验证 + Commit**

### Task 9: 新增风云三国模块（fengyun）
**Files:**
- Create: `models/fengyun_models.py`（或并入 models.py）
- Create: `routers/fengyun.py`, `routers/fengyun_data.py`
- Create: `seed/seed_fengyun.py`
- Create: `templates/fengyun/*.html`
- Modify: `main.py`, `models/models.py`

- [ ] **Step 1: 定义风云模型**（城市/技能/装备/副本/军团/称号/成就）
- [ ] **Step 2: 移植种子生成器**（13 城市/30 技能/105 装备/48 系列/11 名器/14 BOSS/13 副本/15 称号/21 成就/189 物品）
- [ ] **Step 3: 实现路由 + 模板**
- [ ] **Step 4: 注册路由 + 验证**
- [ ] **Step 5: Commit**

### Task 10: 新增幻想西游模块（xyou）
**Files:**
- Create: `models/xyou_models.py`
- Create: `routers/xyou.py`, `routers/xyou_data.py`
- Create: `seed/seed_xyou.py`
- Create: `templates/xyou/*.html`
- Modify: `main.py`, `models/models.py`

- [ ] **Step 1: 定义西游模型**（场景/技能/装备/副本/宠物/药品/材料/坐标）
- [ ] **Step 2: 移植种子生成器**（10 场景/45 技能/108 装备/8 龙宫叉/22 副本/13 宠物/116 物品/14 药品/19 材料/12 坐标）
- [ ] **Step 3: 实现路由 + 模板**
- [ ] **Step 4: 注册路由 + 验证**
- [ ] **Step 5: Commit**

### Task 11: 全量模拟运行验证
**Files:**
- Test: `tests/test_smoke.py`

- [ ] **Step 1: 写冒烟测试**（登录 + 8 款游戏首页 + 关键数据路由）
- [ ] **Step 2: 运行全部测试**
- [ ] **Step 3: 启动服务 curl 冒烟**
- [ ] **Step 4: Commit `v0.3.0` 迁移完成**

---

## 自检
- 覆盖 8 款游戏全部迁移（Task 3-10）
- 多货币钱包接入（Task 2）
- 无占位符，每步含代码/命令/预期
- 类型一致性：统一使用 qqgames 的同步 Session、`utils.common.change_currency`、JWT 认证