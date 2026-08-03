from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import random
import json
from datetime import datetime

from models.database import get_db
from models.models import (
    User, JingwuRole, JingwuDungeon, JingwuEquipment, JingwuItem,
    JingwuFabao, JingwuWuhun, Notification, BattleLog, Wallet
)
from utils.auth import get_current_user
from utils.i18n import t
from utils.jingwutang import (
    create_jingwu_character, calculate_stats, calculate_combat_power,
    start_training, stop_training, process_training, simulate_battle,
    allocate_point, get_training_time_remaining, PROFESSIONS, FABAO_LIST,
    DUNGEON_STAGES, TRANSFER_PATHS, do_transfer, upgrade_polaris, use_item,
    enhance_equipment, socket_gem, forge_divine_equipment, equip_item,
    DIVINE_EQUIPMENT_RECIPES, POLARIS_STARS, EQUIPMENT_SLOTS, QUALITY_COLORS,
    get_item_quantity
)

router = APIRouter(prefix="/jingwutang", tags=["jingwutang"])
templates = Jinja2Templates(directory="templates")


def get_common_context(request: Request, db: Session):
    user = get_current_user(request, db)
    if not user:
        return None
    lang = user.language or "zh"
    theme = user.theme or "light"
    unread_count = db.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.is_read == False
    ).count()
    return {
        "request": request,
        "user": user,
        "lang": lang,
        "theme": theme,
        "_": lambda key: t(key, lang),
        "unread_count": unread_count,
        "now": datetime.utcnow(),
    }


def require_character(ctx, db: Session):
    if not ctx["user"].jw_role:
        return RedirectResponse(url="/jingwutang/create", status_code=302)
    process_training(ctx["user"].jw_role, db)
    return None


@router.get("", response_class=HTMLResponse)
async def jingwutang_home(request: Request, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    role = ctx["user"].jw_role
    training_remaining = get_training_time_remaining(role)
    
    opponents = db.query(JingwuRole).filter(
        JingwuRole.user_id != ctx["user"].id,
        JingwuRole.level >= role.level - 5,
        JingwuRole.level <= role.level + 10
    ).order_by(func.random()).limit(10).all()
    
    if len(opponents) < 3:
        opponents = db.query(JingwuRole).filter(
            JingwuRole.user_id != ctx["user"].id
        ).order_by(func.random()).limit(10).all()
    
    dungeon = db.query(JingwuDungeon).filter(JingwuDungeon.role_id == role.id).first()
    
    ctx.update({
        "role": role,
        "training_remaining": training_remaining,
        "opponents": opponents,
        "stats": calculate_stats(role),
        "dungeon": dungeon,
        "dungeon_stages": DUNGEON_STAGES,
        "transfer_paths": TRANSFER_PATHS,
    })
    return templates.TemplateResponse("jingwutang/index.html", ctx)


@router.get("/create", response_class=HTMLResponse)
async def create_character_page(request: Request, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    if ctx["user"].jw_role:
        return RedirectResponse(url="/jingwutang", status_code=302)
    
    return templates.TemplateResponse("jingwutang/create.html", ctx)


@router.post("/create")
async def create_character(
    request: Request,
    name: str = Form(...),
    gender: str = Form("male"),
    db: Session = Depends(get_db)
):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    if ctx["user"].jw_role:
        return RedirectResponse(url="/jingwutang", status_code=302)
    
    create_jingwu_character(db, ctx["user"], name, gender)
    return RedirectResponse(url="/jingwutang", status_code=302)


@router.get("/battle/{opponent_id}")
async def battle(request: Request, opponent_id: int, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    attacker = ctx["user"].jw_role
    defender = db.query(JingwuRole).filter(JingwuRole.id == opponent_id).first()
    
    if not defender or defender.id == attacker.id:
        return RedirectResponse(url="/jingwutang", status_code=302)
    
    if attacker.stamina < 10:
        ctx["message"] = "体力不足！"
        ctx["message_type"] = "error"
        ctx.update({
            "role": attacker,
            "training_remaining": get_training_time_remaining(attacker),
            "opponents": [],
            "stats": calculate_stats(attacker),
        })
        return templates.TemplateResponse("jingwutang/index.html", ctx)
    
    attacker.stamina = max(0, attacker.stamina - 10)
    result = simulate_battle(attacker, defender, db)
    
    ctx.update({
        "role": attacker,
        "opponent": defender,
        "result": result,
        "battle_log": result["log"],
    })
    return templates.TemplateResponse("jingwutang/battle.html", ctx)


@router.post("/training/start")
async def do_start_training(
    request: Request,
    training_type: str = Form("workshop"),
    hours: int = Form(4),
    db: Session = Depends(get_db)
):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    start_training(ctx["user"].jw_role, training_type, min(hours, 8))
    db.commit()
    return RedirectResponse(url="/jingwutang", status_code=302)


@router.get("/training/stop")
async def do_stop_training(request: Request, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    stop_training(ctx["user"].jw_role, db)
    return RedirectResponse(url="/jingwutang", status_code=302)


@router.get("/attributes", response_class=HTMLResponse)
async def attributes(request: Request, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    role = ctx["user"].jw_role
    stats = calculate_stats(role)
    training_remaining = get_training_time_remaining(role)
    
    ctx.update({
        "role": role,
        "stats": stats,
        "training_remaining": training_remaining,
        "professions": PROFESSIONS,
        "transfer_paths": TRANSFER_PATHS,
    })
    return templates.TemplateResponse("jingwutang/attributes.html", ctx)


@router.post("/attributes/allocate")
async def do_allocate(
    request: Request,
    stat: str = Form(...),
    db: Session = Depends(get_db)
):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    allocate_point(ctx["user"].jw_role, stat, db)
    return RedirectResponse(url="/jingwutang/attributes", status_code=302)


@router.post("/transfer")
async def do_transfer_route(
    request: Request,
    path: str = Form(...),
    db: Session = Depends(get_db)
):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    do_transfer(ctx["user"].jw_role, path, db)
    return RedirectResponse(url="/jingwutang/attributes", status_code=302)


@router.get("/inventory", response_class=HTMLResponse)
async def inventory(request: Request, category: str = "all", db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    role = ctx["user"].jw_role
    items_query = role.items
    
    categories = ["equipment", "prop", "gem", "shenbing", "blueprint", "mold", "material", "other"]
    category_names = {
        "equipment": "装备",
        "prop": "道具",
        "gem": "宝石",
        "shenbing": "神兵",
        "blueprint": "图纸",
        "mold": "模具",
        "material": "材料",
        "other": "其他",
    }
    
    if category != "all":
        items = [i for i in items_query if i.item_type == category or i.category == category]
    else:
        items = list(items_query)
    
    ctx.update({
        "role": role,
        "items": items,
        "current_category": category,
        "categories": categories,
        "category_names": category_names,
        "total_items": len(items_query),
        "max_items": 480,
    })
    return templates.TemplateResponse("jingwutang/inventory.html", ctx)


@router.get("/item/use/{item_id}")
async def do_use_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    use_item(ctx["user"].jw_role, item_id, db)
    return RedirectResponse(url="/jingwutang/inventory", status_code=302)


@router.get("/equipment", response_class=HTMLResponse)
async def equipment(request: Request, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    role = ctx["user"].jw_role
    equipped = {}
    unequipped = []
    
    for eq in role.equipments:
        if eq.is_equipped:
            equipped[eq.slot] = eq
        else:
            unequipped.append(eq)
    
    tianquan_count = get_item_quantity(role, "天权强化符")
    yaoguang_count = get_item_quantity(role, "摇光宝石符")
    gems = [i for i in role.items if i.category == "gem"]
    
    ctx.update({
        "role": role,
        "equipped": equipped,
        "unequipped": unequipped,
        "equipment_slots": EQUIPMENT_SLOTS,
        "quality_colors": QUALITY_COLORS,
        "stats": calculate_stats(role),
        "tianquan_count": tianquan_count,
        "yaoguang_count": yaoguang_count,
        "gems": gems,
    })
    return templates.TemplateResponse("jingwutang/equipment.html", ctx)


@router.get("/equipment/equip/{equip_id}")
async def do_equip(request: Request, equip_id: int, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    equip_item(ctx["user"].jw_role, equip_id, db)
    return RedirectResponse(url="/jingwutang/equipment", status_code=302)


@router.get("/equipment/enhance/{equip_id}")
async def do_enhance(request: Request, equip_id: int, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    enhance_equipment(ctx["user"].jw_role, equip_id, db)
    return RedirectResponse(url="/jingwutang/equipment", status_code=302)


@router.get("/equipment/socket/{equip_id}/{gem_name}")
async def do_socket(request: Request, equip_id: int, gem_name: str, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    socket_gem(ctx["user"].jw_role, equip_id, gem_name, db)
    return RedirectResponse(url="/jingwutang/equipment", status_code=302)


@router.get("/forge", response_class=HTMLResponse)
async def forge(request: Request, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    role = ctx["user"].jw_role
    
    materials = {
        "千年玄玉": get_item_quantity(role, "千年玄玉"),
        "千年灵玉": get_item_quantity(role, "千年灵玉"),
        "神装图纸": get_item_quantity(role, "神装图纸"),
        "神铸模具": get_item_quantity(role, "神铸模具"),
    }
    
    ctx.update({
        "role": role,
        "recipes": DIVINE_EQUIPMENT_RECIPES,
        "materials": materials,
    })
    return templates.TemplateResponse("jingwutang/forge.html", ctx)


@router.get("/forge/{recipe_id}")
async def do_forge(request: Request, recipe_id: int, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    forge_divine_equipment(ctx["user"].jw_role, recipe_id, db)
    return RedirectResponse(url="/jingwutang/forge", status_code=302)


@router.get("/fabao", response_class=HTMLResponse)
async def fabao(request: Request, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    role = ctx["user"].jw_role
    
    ctx.update({
        "role": role,
        "fabaos": role.fabaos,
        "fabao_list": FABAO_LIST,
    })
    return templates.TemplateResponse("jingwutang/fabao.html", ctx)


@router.get("/wuhun", response_class=HTMLResponse)
async def wuhun(request: Request, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    role = ctx["user"].jw_role
    
    wuhun_data = []
    for w in role.wuhuns:
        try:
            stats_list = json.loads(w.stats) if w.stats else []
        except:
            stats_list = []
        wuhun_data.append({
            "wuhun": w,
            "stats": stats_list,
        })
    
    ctx.update({
        "role": role,
        "wuhun_data": wuhun_data,
    })
    return templates.TemplateResponse("jingwutang/wuhun.html", ctx)


@router.get("/polaris", response_class=HTMLResponse)
async def polaris(request: Request, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    role = ctx["user"].jw_role
    polaris_count = get_item_quantity(role, "北极星")
    
    star_items = {}
    for star in POLARIS_STARS:
        star_items[star["name_zh"]] = get_item_quantity(role, star["item"])
    
    ctx.update({
        "role": role,
        "polaris_count": polaris_count,
        "polaris_stars": POLARIS_STARS,
        "star_items": star_items,
    })
    return templates.TemplateResponse("jingwutang/polaris.html", ctx)


@router.get("/polaris/upgrade")
async def do_upgrade_polaris(request: Request, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    upgrade_polaris(ctx["user"].jw_role, db)
    return RedirectResponse(url="/jingwutang/polaris", status_code=302)


@router.get("/dungeon", response_class=HTMLResponse)
async def dungeon(request: Request, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    role = ctx["user"].jw_role
    dungeon = db.query(JingwuDungeon).filter(JingwuDungeon.role_id == role.id).first()
    
    ctx.update({
        "role": role,
        "dungeon": dungeon,
        "stages": DUNGEON_STAGES,
    })
    return templates.TemplateResponse("jingwutang/dungeon.html", ctx)


@router.get("/dungeon/fight/{stage_id}")
async def dungeon_fight(request: Request, stage_id: int, db: Session = Depends(get_db)):
    ctx = get_common_context(request, db)
    if not ctx:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    redirect = require_character(ctx, db)
    if redirect:
        return redirect
    
    role = ctx["user"].jw_role
    dungeon = db.query(JingwuDungeon).filter(JingwuDungeon.role_id == role.id).first()
    
    stage = None
    for s in DUNGEON_STAGES:
        if s["id"] == stage_id:
            stage = s
            break
    
    if not stage or role.level < stage["level_req"]:
        return RedirectResponse(url="/jingwutang/dungeon", status_code=302)
    
    if dungeon.daily_attempts <= 0:
        return RedirectResponse(url="/jingwutang/dungeon", status_code=302)
    
    dungeon.daily_attempts -= 1
    
    boss_role = JingwuRole(
        name=stage["boss"],
        level=stage["level_req"] + 5,
    )
    boss_role.max_hp = 500 + stage["level_req"] * 100
    boss_role.hp = boss_role.max_hp
    boss_role.base_damage = 20 + stage["level_req"] * 3
    boss_role.base_defense = 10 + stage["level_req"] * 2
    boss_role.base_speed = 15 + stage["level_req"]
    boss_role.base_dodge = 30
    boss_role.base_crit = 10
    boss_role.user = ctx["user"]
    
    result = simulate_battle(role, boss_role, db, is_dungeon=True)
    
    if result["winner"] == role:
        dungeon.stage = min(dungeon.stage + 1, len(DUNGEON_STAGES))
    
    db.commit()
    
    ctx.update({
        "role": role,
        "stage": stage,
        "result": result,
        "battle_log": result["log"],
    })
    return templates.TemplateResponse("jingwutang/dungeon_battle.html", ctx)


@router.get("/refresh-opponents")
async def refresh_opponents(request: Request, db: Session = Depends(get_db)):
    return RedirectResponse(url="/jingwutang", status_code=302)
