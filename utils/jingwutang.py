import random
import math
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.models import (
    JingwuRole, JingwuItem, JingwuEquipment, JingwuFabao, 
    JingwuWuhun, JingwuDungeon, BattleLog, User
)

TRANSFER_PATHS = {
    "shen": {
        "name_zh": "神",
        "name_en": "Deity",
        "req_level": 80,
        "bonus": {"damage": 1.3, "defense": 1.2, "hp": 1.3},
        "description_zh": "神，高高在上，主宰万物",
        "description_en": "Deity, supreme ruler",
        "color": "#ffd700"
    },
    "mo": {
        "name_zh": "魔",
        "name_en": "Demon",
        "req_level": 80,
        "bonus": {"damage": 1.5, "crit": 1.4, "speed": 1.2},
        "description_zh": "魔，随心所欲，唯我独尊",
        "description_en": "Demon, unfettered power",
        "color": "#9b59b6"
    },
    "xian": {
        "name_zh": "仙",
        "name_en": "Immortal",
        "req_level": 80,
        "bonus": {"hp": 1.4, "mp": 1.5, "dodge": 1.3, "defense": 1.2},
        "description_zh": "仙，飘逸出尘，长生不老",
        "description_en": "Immortal, eternal and free",
        "color": "#3498db"
    }
}

PROFESSIONS = {
    "common": {"name_zh": "普通", "name_en": "Common", "req_level": 1},
    "swordsman": {"name_zh": "剑客", "name_en": "Swordsman", "req_level": 20},
    "blade": {"name_zh": "刀客", "name_en": "Blade Master", "req_level": 20},
    "fist": {"name_zh": "拳师", "name_en": "Brawler", "req_level": 20},
    "assassin": {"name_zh": "刺客", "name_en": "Assassin", "req_level": 40},
    "mage": {"name_zh": "术士", "name_en": "Mage", "req_level": 40},
    "healer": {"name_zh": "医师", "name_en": "Healer", "req_level": 40},
}

FABAO_LIST = [
    {"slot": 1, "name_zh": "圣盾", "name_en": "Holy Shield", "stat": "defense"},
    {"slot": 2, "name_zh": "血速", "name_en": "Blood Swift", "stat": "hp_speed"},
    {"slot": 3, "name_zh": "闪击", "name_en": "Flash Strike", "stat": "dodge_crit"},
    {"slot": 4, "name_zh": "致命", "name_en": "Deadly", "stat": "crit"},
    {"slot": 5, "name_zh": "精准", "name_en": "Precision", "stat": "accuracy"},
    {"slot": 6, "name_zh": "韧性", "name_en": "Tenacity", "stat": "toughness"},
    {"slot": 7, "name_zh": "必杀", "name_en": "Kill Strike", "stat": "crit_damage"},
    {"slot": 8, "name_zh": "破防", "name_en": "Armor Break", "stat": "armor_pen"},
    {"slot": 9, "name_zh": "减暴伤", "name_en": "Crit Resist", "stat": "crit_reduce"},
]

WUHUN_ELEMENTS = [
    {"element": "earth", "slot": 1, "name_zh": "顶阶土魂", "name_en": "Supreme Earth Soul", "req_level": 1},
    {"element": "water", "slot": 2, "name_zh": "顶阶水魂", "name_en": "Supreme Water Soul", "req_level": 1},
    {"element": "fire", "slot": 3, "name_zh": "火魂", "name_en": "Fire Soul", "req_level": 40},
    {"element": "gold", "slot": 4, "name_zh": "金魂", "name_en": "Gold Soul", "req_level": 50},
    {"element": "wood", "slot": 5, "name_zh": "木魂", "name_en": "Wood Soul", "req_level": 60},
]

DUNGEON_STAGES = [
    {"chapter": 1, "stage": 1, "id": 11, "name_zh": "黄巾之乱", "name_en": "Yellow Turban", "boss": "程远志", "level_req": 20, "drops": ["千年玄玉", "天权强化符", "小还丹"]},
    {"chapter": 1, "stage": 2, "id": 12, "name_zh": "讨伐董卓", "name_en": "Dong Zhuo", "boss": "华雄", "level_req": 30, "drops": ["千年玄玉", "千年灵玉", "摇光宝石符", "大还丹"]},
    {"chapter": 1, "stage": 3, "id": 13, "name_zh": "三英战吕布", "name_en": "Lu Bu", "boss": "吕布", "level_req": 40, "drops": ["千年玄玉", "千年灵玉", "北极星", "天玑命力符"]},
    {"chapter": 2, "stage": 1, "id": 21, "name_zh": "官渡之战", "name_en": "Guandu", "boss": "颜良", "level_req": 50, "drops": ["千年玄玉", "千年灵玉", "北极星", "精炼魔石"]},
    {"chapter": 2, "stage": 2, "id": 22, "name_zh": "赤壁之战", "name_en": "Chibi", "boss": "曹操", "level_req": 60, "drops": ["千年玄玉", "千年灵玉", "北极星", "精炼灵石"]},
    {"chapter": 2, "stage": 3, "id": 23, "name_zh": "夷陵之战", "name_en": "Yiling", "boss": "陆逊", "level_req": 70, "drops": ["千年玄玉", "千年灵玉", "北极星", "神装图纸"]},
    {"chapter": 3, "stage": 1, "id": 31, "name_zh": "六出祁山", "name_en": "Qishan", "boss": "司马懿", "level_req": 80, "drops": ["千年玄玉", "千年灵玉", "北极星", "神铸模具"]},
]

EQUIPMENT_SLOTS = {
    "weapon": {"name_zh": "武器", "name_en": "Weapon"},
    "helmet": {"name_zh": "头盔", "name_en": "Helmet"},
    "armor": {"name_zh": "铠甲", "name_en": "Armor"},
    "boots": {"name_zh": "战靴", "name_en": "Boots"},
    "ring": {"name_zh": "戒指", "name_en": "Ring"},
    "necklace": {"name_zh": "项链", "name_en": "Necklace"},
}

QUALITY_COLORS = {
    "common": "#95a5a6",
    "good": "#2ecc71",
    "excellent": "#3498db",
    "epic": "#9b59b6",
    "legendary": "#f39c12",
    "divine": "#e74c3c",
}

POLARIS_STARS = [
    {"name_zh": "天枢", "name_en": "Tianshu", "item": "天枢魔晶符", "stat": "法宝强化"},
    {"name_zh": "天璇", "name_en": "Tianxuan", "item": "天璇魂力符", "stat": "武魂强化"},
    {"name_zh": "天玑", "name_en": "Tianji", "item": "天玑命力符", "stat": "生命强化"},
    {"name_zh": "天权", "name_en": "Tianquan", "item": "天权强化符", "stat": "装备强化"},
    {"name_zh": "玉衡", "name_en": "Yuheng", "item": "玉衡灵符", "stat": "灵力强化"},
    {"name_zh": "开阳", "name_en": "Kaiyang", "item": "开阳罡符", "stat": "罡气强化"},
    {"name_zh": "摇光", "name_en": "Yaoguang", "item": "摇光宝石符", "stat": "宝石镶嵌"},
]

DIVINE_EQUIPMENT_RECIPES = [
    {"name": "神·青龙偃月刀", "slot": "weapon", "quality": "divine", "damage": 500, "crit": 20, "req_jade": 10, "req_spirit": 5},
    {"name": "神·方天画戟", "slot": "weapon", "quality": "divine", "damage": 600, "speed": 50, "req_jade": 15, "req_spirit": 8},
    {"name": "神·诸葛羽扇", "slot": "weapon", "quality": "divine", "damage": 300, "hp": 2000, "mp": 500, "req_jade": 10, "req_spirit": 10},
    {"name": "神·麒麟铠", "slot": "armor", "quality": "divine", "defense": 300, "hp": 3000, "req_jade": 12, "req_spirit": 6},
    {"name": "神·的卢马", "slot": "boots", "quality": "divine", "speed": 200, "dodge": 30, "req_jade": 8, "req_spirit": 4},
    {"name": "神·传国玉玺", "slot": "necklace", "quality": "divine", "hp": 5000, "crit_damage": 50, "req_jade": 20, "req_spirit": 15},
]

INITIAL_ITEMS = [
    {"item_type": "prop", "category": "prop", "name_zh": "战神黄金令牌", "name_en": "War God Gold Token", "quantity": 100, "quality": "epic", "desc_zh": "战神宫的信物", "desc_en": "War God Palace token"},
    {"item_type": "material", "category": "material", "name_zh": "天枢魔晶符", "name_en": "Tianshu Magic Crystal", "quantity": 7000, "quality": "excellent", "desc_zh": "北斗第一天枢，强化法宝", "desc_en": "Enhance artifacts"},
    {"item_type": "material", "category": "material", "name_zh": "天璇魂力符", "name_en": "Tianxuan Soul Force", "quantity": 7000, "quality": "excellent", "desc_zh": "北斗第二天璇，提升魂力", "desc_en": "Boost soul power"},
    {"item_type": "material", "category": "material", "name_zh": "天玑命力符", "name_en": "Tianji Life Force", "quantity": 7000, "quality": "excellent", "desc_zh": "北斗第三天玑，增强生命", "desc_en": "Boost life force"},
    {"item_type": "material", "category": "material", "name_zh": "天权强化符", "name_en": "Tianquan Enhance", "quantity": 7000, "quality": "excellent", "desc_zh": "北斗第四天权，强化装备", "desc_en": "Enhance equipment"},
    {"item_type": "material", "category": "material", "name_zh": "玉衡灵符", "name_en": "Yuheng Spirit", "quantity": 5000, "quality": "excellent", "desc_zh": "北斗第五玉衡，提升灵力", "desc_en": "Boost spirit"},
    {"item_type": "material", "category": "material", "name_zh": "开阳罡符", "name_en": "Kaiyang Gang", "quantity": 5000, "quality": "excellent", "desc_zh": "北斗第六开阳，增加罡气", "desc_en": "Boost gang qi"},
    {"item_type": "material", "category": "material", "name_zh": "摇光宝石符", "name_en": "Yaoguang Gem", "quantity": 7000, "quality": "excellent", "desc_zh": "北斗第七摇光，镶嵌宝石", "desc_en": "Socket gems"},
    {"item_type": "material", "category": "material", "name_zh": "北极星", "name_en": "Polaris Star", "quantity": 100, "quality": "legendary", "desc_zh": "北斗至尊，北极星之辉，可大幅提升属性", "desc_en": "Supreme Polaris, grants great power"},
    {"item_type": "material", "category": "material", "name_zh": "精炼魔石", "name_en": "Refine Magic Stone", "quantity": 50, "quality": "epic", "desc_zh": "用于精炼装备", "desc_en": "Refine equipment"},
    {"item_type": "material", "category": "material", "name_zh": "精炼灵石", "name_en": "Refine Spirit Stone", "quantity": 10, "quality": "legendary", "desc_zh": "高级精炼材料", "desc_en": "High-grade refine material"},
    {"item_type": "material", "category": "material", "name_zh": "千年玄玉", "name_en": "Millennium Black Jade", "quantity": 5, "quality": "legendary", "desc_zh": "三国副本掉落，锻造神级装备必备", "desc_en": "From Three Kingdoms dungeon, for divine gear"},
    {"item_type": "material", "category": "material", "name_zh": "千年灵玉", "name_en": "Millennium Spirit Jade", "quantity": 5, "quality": "legendary", "desc_zh": "三国副本掉落，锻造神级装备必备", "desc_en": "From Three Kingdoms dungeon, for divine gear"},
    {"item_type": "blueprint", "category": "blueprint", "name_zh": "神装图纸", "name_en": "Divine Blueprint", "quantity": 1, "quality": "legendary", "desc_zh": "锻造神级装备的图纸", "desc_en": "Blueprint for divine equipment"},
    {"item_type": "mold", "category": "mold", "name_zh": "神铸模具", "name_en": "Divine Mold", "quantity": 1, "quality": "legendary", "desc_zh": "锻造神级装备的模具", "desc_en": "Mold for divine equipment"},
    {"item_type": "gem", "category": "gem", "name_zh": "红宝石", "name_en": "Ruby", "quantity": 10, "quality": "excellent", "desc_zh": "镶嵌武器，增加伤害", "desc_en": "Socket in weapon for damage"},
    {"item_type": "gem", "category": "gem", "name_zh": "蓝宝石", "name_en": "Sapphire", "quantity": 10, "quality": "excellent", "desc_zh": "镶嵌防具，增加防御", "desc_en": "Socket in armor for defense"},
    {"item_type": "gem", "category": "gem", "name_zh": "绿宝石", "name_en": "Emerald", "quantity": 10, "quality": "excellent", "desc_zh": "镶嵌鞋子，增加闪避", "desc_en": "Socket in boots for dodge"},
    {"item_type": "prop", "category": "prop", "name_zh": "大力神丸", "name_en": "Power Pill", "quantity": 100, "quality": "excellent", "desc_zh": "恢复体力", "desc_en": "Restore stamina"},
    {"item_type": "prop", "category": "prop", "name_zh": "变性灵玉", "name_en": "Gender Jade", "quantity": 1, "quality": "legendary", "desc_zh": "可以改变性别", "desc_en": "Change gender"},
    {"item_type": "prop", "category": "prop", "name_zh": "小还丹", "name_en": "Minor Revival Pill", "quantity": 50, "quality": "good", "desc_zh": "恢复少量气血", "desc_en": "Restore some HP"},
    {"item_type": "prop", "category": "prop", "name_zh": "大还丹", "name_en": "Major Revival Pill", "quantity": 20, "quality": "excellent", "desc_zh": "恢复大量气血", "desc_en": "Restore much HP"},
    {"item_type": "prop", "category": "prop", "name_zh": "雪参玉蟾丸", "name_en": "Ginseng Toad Pill", "quantity": 5, "quality": "epic", "desc_zh": "恢复全部气血和精气", "desc_en": "Restore all HP and MP"},
]


def calculate_exp_for_level(level: int) -> int:
    return int(100 * math.pow(1.15, level - 1))


def calculate_combat_power(role: JingwuRole) -> int:
    base = role.base_damage * 2 + role.base_defense * 1.5 + role.base_speed + role.max_hp // 10
    attr_bonus = (role.str_point * 5 + role.con_point * 3 + role.agi_point * 2 + role.def_point * 2 + role.mag_point * 2)
    level_bonus = role.level * 50
    polaris_bonus = role.polaris_level * 200
    
    equip_bonus = 0
    for eq in role.equipments:
        if eq.is_equipped:
            enhance_mult = 1 + eq.enhance_level * 0.1
            equip_bonus += (eq.damage * enhance_mult * 2 + eq.defense * enhance_mult * 1.5 + eq.hp // 10 + eq.speed)
    
    transfer_bonus = 1.5 if role.transferred else 1.0
    return int((base + attr_bonus + level_bonus + polaris_bonus + equip_bonus) * transfer_bonus)


def calculate_stats(role: JingwuRole):
    hp = 100 + role.level * 20 + role.con_point * 15
    mp = 50 + role.level * 5 + role.mag_point * 8
    damage = 10 + role.level * 3 + role.str_point * 5
    defense = 5 + role.level * 2 + role.def_point * 3
    speed = 10 + role.level + role.agi_point * 2
    accuracy = 100 + role.level * 2 + role.agi_point
    dodge = 50 + role.level + role.agi_point * 2
    crit = 5 + role.level * 0.2 + role.str_point * 0.1
    crit_damage = 150 + role.str_point

    for eq in role.equipments:
        if eq.is_equipped:
            enhance_mult = 1 + eq.enhance_level * 0.1
            damage += int(eq.damage * enhance_mult)
            defense += int(eq.defense * enhance_mult)
            hp += int(eq.hp * enhance_mult)
            speed += int(eq.speed * enhance_mult)
            accuracy += eq.accuracy
            dodge += eq.dodge
            crit += eq.crit
            crit_damage += eq.crit_damage

    if role.transferred and role.transfer_path in TRANSFER_PATHS:
        bonus = TRANSFER_PATHS[role.transfer_path]["bonus"]
        if "damage" in bonus: damage = int(damage * bonus["damage"])
        if "defense" in bonus: defense = int(defense * bonus["defense"])
        if "hp" in bonus: hp = int(hp * bonus["hp"])
        if "mp" in bonus: mp = int(mp * bonus["mp"])
        if "speed" in bonus: speed = int(speed * bonus["speed"])
        if "crit" in bonus: crit = min(95, crit * bonus["crit"])
        if "dodge" in bonus: dodge = int(dodge * bonus["dodge"])

    if role.polaris_level > 0:
        polaris_bonus = 1 + role.polaris_level * 0.05
        damage = int(damage * polaris_bonus)
        defense = int(defense * polaris_bonus)
        hp = int(hp * polaris_bonus)

    return {
        "hp": int(hp),
        "mp": int(mp),
        "max_hp": int(hp),
        "max_mp": int(mp),
        "damage": int(damage),
        "defense": int(defense),
        "speed": int(speed),
        "accuracy": int(accuracy),
        "dodge": int(dodge),
        "crit": min(95, int(crit)),
        "crit_damage": int(crit_damage),
        "counter": int(10 + role.agi_point * 0.5),
        "lifesteal": int(5 + role.str_point * 0.2),
    }


def get_item_quantity(role: JingwuRole, item_name: str) -> int:
    for item in role.items:
        if item.name == item_name:
            return item.quantity
    return 0


def add_item(role: JingwuRole, item_name: str, quantity: int, quality: str = "common", db: Session = None):
    existing = None
    for item in role.items:
        if item.name == item_name:
            existing = item
            break
    if existing:
        existing.quantity += quantity
    else:
        item_info = None
        for init_item in INITIAL_ITEMS:
            if init_item["name_zh"] == item_name:
                item_info = init_item
                break
        
        new_item = JingwuItem(
            owner_id=role.id,
            item_type=item_info["item_type"] if item_info else "material",
            category=item_info["category"] if item_info else "material",
            name=item_name,
            description=item_info["desc_zh"] if item_info else "",
            quantity=quantity,
            quality=item_info["quality"] if item_info else quality,
        )
        db.add(new_item)


def consume_item(role: JingwuRole, item_name: str, quantity: int, db: Session) -> bool:
    for item in role.items:
        if item.name == item_name:
            if item.quantity >= quantity:
                item.quantity -= quantity
                if item.quantity <= 0:
                    db.delete(item)
                return True
            return False
    return False


def create_jingwu_character(db: Session, user: User, name: str, gender: str = "male"):
    role = JingwuRole(
        user_id=user.id,
        name=name,
        gender=gender,
        profession="common",
        potential=3,
    )
    db.add(role)
    db.flush()

    dungeon = JingwuDungeon(role_id=role.id)
    db.add(dungeon)
    
    for fabao_data in FABAO_LIST:
        fabao = JingwuFabao(
            owner_id=role.id,
            slot=fabao_data["slot"],
            name=fabao_data["name_zh"],
            level=1,
            proficiency=0,
            quality="common",
            stat_type=fabao_data["stat"],
            stat_value=fabao_data["slot"] * 10 if fabao_data["slot"] <= 7 else 0,
        )
        db.add(fabao)
    
    for wuhun_data in WUHUN_ELEMENTS[:2]:
        if wuhun_data["element"] == "earth":
            stats_list = [
                {"name_zh": "命中", "name_en": "ACC", "value": 1100, "quality": "legendary", "stars": 5},
                {"name_zh": "伤害", "name_en": "DMG", "value": 2000, "quality": "legendary", "stars": 5},
                {"name_zh": "速度", "name_en": "SPD", "value": 400, "quality": "legendary", "stars": 5},
                {"name_zh": "闪避", "name_en": "Dodge", "value": 1400, "quality": "legendary", "stars": 5},
                {"name_zh": "格挡", "name_en": "Block", "value": 10, "quality": "common", "stars": 1},
            ]
        else:
            stats_list = [
                {"name_zh": "抗反击", "name_en": "Counter Resist", "value": 37, "quality": "common", "stars": 1},
                {"name_zh": "暴击", "name_en": "Crit", "value": 32, "quality": "common", "stars": 1},
                {"name_zh": "气血", "name_en": "HP", "value": 109, "quality": "common", "stars": 2},
                {"name_zh": "减暴伤", "name_en": "Crit Resist", "value": 42, "quality": "common", "stars": 1},
                {"name_zh": "暴击伤害", "name_en": "Crit DMG", "value": 42, "quality": "common", "stars": 1},
                {"name_zh": "伤害", "name_en": "DMG", "value": 2000, "quality": "legendary", "stars": 5},
            ]
        wuhun = JingwuWuhun(
            owner_id=role.id,
            element=wuhun_data["element"],
            slot=wuhun_data["slot"],
            name=wuhun_data["name_zh"],
            level=0,
            quality="legendary",
            stats=json.dumps(stats_list, ensure_ascii=False),
        )
        db.add(wuhun)
    
    starter_weapon = JingwuEquipment(
        owner_id=role.id,
        slot="weapon",
        name="新手木剑",
        level_required=1,
        quality="common",
        damage=5,
        is_equipped=True,
        gem_slots=1,
    )
    db.add(starter_weapon)
    
    starter_armor = JingwuEquipment(
        owner_id=role.id,
        slot="armor",
        name="粗布衣",
        level_required=1,
        quality="common",
        defense=3,
        hp=50,
        is_equipped=True,
        gem_slots=1,
    )
    db.add(starter_armor)
    
    for item_data in INITIAL_ITEMS:
        item = JingwuItem(
            owner_id=role.id,
            item_type=item_data["item_type"],
            category=item_data["category"],
            name=item_data["name_zh"],
            description=item_data.get("desc_zh", ""),
            quantity=item_data["quantity"],
            quality=item_data["quality"],
        )
        db.add(item)
    
    stats = calculate_stats(role)
    role.max_hp = stats["max_hp"]
    role.hp = stats["hp"]
    role.max_mp = stats["max_mp"]
    role.mp = stats["mp"]
    role.base_damage = stats["damage"]
    role.base_defense = stats["defense"]
    role.base_speed = stats["speed"]
    role.base_accuracy = stats["accuracy"]
    role.base_dodge = stats["dodge"]
    role.base_crit = stats["crit"]
    role.base_crit_damage = stats["crit_damage"]
    role.combat_power = calculate_combat_power(role)
    
    db.commit()
    db.refresh(role)
    return role


def do_transfer(role: JingwuRole, path: str, db: Session):
    if role.level < 80 or role.transferred:
        return False
    if path not in TRANSFER_PATHS:
        return False
    
    role.transferred = True
    role.transfer_path = path
    role.transfer_name = TRANSFER_PATHS[path]["name_zh"]
    role.potential += 50
    
    stats = calculate_stats(role)
    role.max_hp = stats["max_hp"]
    role.hp = stats["hp"]
    role.max_mp = stats["max_mp"]
    role.mp = stats["mp"]
    role.base_damage = stats["damage"]
    role.base_defense = stats["defense"]
    role.base_speed = stats["speed"]
    role.combat_power = calculate_combat_power(role)
    
    db.commit()
    return True


def upgrade_polaris(role: JingwuRole, db: Session):
    polaris_item = None
    for item in role.items:
        if item.name == "北极星" and item.quantity > 0:
            polaris_item = item
            break
    
    if not polaris_item:
        return False, "需要北极星"
    
    polaris_item.quantity -= 1
    if polaris_item.quantity <= 0:
        db.delete(polaris_item)
    
    role.polaris_level += 1
    role.polaris_exp += 1000
    stats = calculate_stats(role)
    role.max_hp = stats["max_hp"]
    role.hp = stats["hp"]
    role.base_damage = stats["damage"]
    role.base_defense = stats["defense"]
    role.combat_power = calculate_combat_power(role)
    
    db.commit()
    return True, f"北极星升级到{role.polaris_level}级！"


def enhance_equipment(role: JingwuRole, equipment_id: int, db: Session):
    eq = db.query(JingwuEquipment).filter(
        JingwuEquipment.id == equipment_id,
        JingwuEquipment.owner_id == role.id
    ).first()
    
    if not eq:
        return False, "装备不存在"
    
    if eq.enhance_level >= 20:
        return False, "已达最高强化等级"
    
    enhance_item_count = 1 + eq.enhance_level // 5
    if not consume_item(role, "天权强化符", enhance_item_count, db):
        return False, f"需要{enhance_item_count}张天权强化符"
    
    success_rate = max(0.3, 1.0 - eq.enhance_level * 0.04)
    if random.random() < success_rate:
        eq.enhance_level += 1
        stats = calculate_stats(role)
        role.max_hp = stats["max_hp"]
        role.base_damage = stats["damage"]
        role.base_defense = stats["defense"]
        role.combat_power = calculate_combat_power(role)
        db.commit()
        return True, f"强化成功！{eq.name}+{eq.enhance_level}"
    else:
        db.commit()
        return False, "强化失败，天权强化符已消耗"


def socket_gem(role: JingwuRole, equipment_id: int, gem_name: str, db: Session):
    eq = db.query(JingwuEquipment).filter(
        JingwuEquipment.id == equipment_id,
        JingwuEquipment.owner_id == role.id
    ).first()
    
    if not eq:
        return False, "装备不存在"
    
    current_gems = json.loads(eq.gems) if eq.gems else []
    if len(current_gems) >= eq.gem_slots:
        return False, "宝石槽已满"
    
    if not consume_item(role, "摇光宝石符", 1, db):
        return False, "需要摇光宝石符"
    
    if not consume_item(role, gem_name, 1, db):
        return False, f"需要{gem_name}"
    
    gem_bonus = {"红宝石": {"damage": 50}, "蓝宝石": {"defense": 30, "hp": 200}, "绿宝石": {"dodge": 10, "speed": 20}}
    bonus = gem_bonus.get(gem_name, {})
    for k, v in bonus.items():
        setattr(eq, k, getattr(eq, k, 0) + v)
    
    current_gems.append(gem_name)
    eq.gems = json.dumps(current_gems, ensure_ascii=False)
    
    stats = calculate_stats(role)
    role.max_hp = stats["max_hp"]
    role.base_damage = stats["damage"]
    role.base_defense = stats["defense"]
    role.combat_power = calculate_combat_power(role)
    
    db.commit()
    return True, f"成功镶嵌{gem_name}！"


def forge_divine_equipment(role: JingwuRole, recipe_index: int, db: Session):
    if recipe_index < 0 or recipe_index >= len(DIVINE_EQUIPMENT_RECIPES):
        return False, "配方不存在"
    
    recipe = DIVINE_EQUIPMENT_RECIPES[recipe_index]
    
    has_blueprint = get_item_quantity(role, "神装图纸") >= 1
    has_mold = get_item_quantity(role, "神铸模具") >= 1
    has_jade = get_item_quantity(role, "千年玄玉") >= recipe["req_jade"]
    has_spirit = get_item_quantity(role, "千年灵玉") >= recipe["req_spirit"]
    
    if not has_blueprint:
        return False, "需要神装图纸"
    if not has_mold:
        return False, "需要神铸模具"
    if not has_jade:
        return False, f"需要{recipe['req_jade']}个千年玄玉"
    if not has_spirit:
        return False, f"需要{recipe['req_spirit']}个千年灵玉"
    
    consume_item(role, "神装图纸", 1, db)
    consume_item(role, "神铸模具", 1, db)
    consume_item(role, "千年玄玉", recipe["req_jade"], db)
    consume_item(role, "千年灵玉", recipe["req_spirit"], db)
    
    for eq in role.equipments:
        if eq.slot == recipe["slot"] and eq.is_equipped:
            eq.is_equipped = False
    
    new_eq = JingwuEquipment(
        owner_id=role.id,
        slot=recipe["slot"],
        name=recipe["name"],
        level_required=80,
        quality=recipe["quality"],
        damage=recipe.get("damage", 0),
        defense=recipe.get("defense", 0),
        hp=recipe.get("hp", 0),
        speed=recipe.get("speed", 0),
        crit=recipe.get("crit", 0),
        crit_damage=recipe.get("crit_damage", 0),
        dodge=recipe.get("dodge", 0),
        is_equipped=True,
        gem_slots=3,
    )
    db.add(new_eq)
    
    stats = calculate_stats(role)
    role.max_hp = stats["max_hp"]
    role.hp = stats["hp"]
    role.base_damage = stats["damage"]
    role.base_defense = stats["defense"]
    role.base_speed = stats["speed"]
    role.combat_power = calculate_combat_power(role)
    
    db.commit()
    return True, f"锻造成功！获得{recipe['name']}"


def upgrade_star(role: JingwuRole, star_index: int, db: Session):
    if star_index < 0 or star_index >= len(POLARIS_STARS):
        return False, "无效的星位"
    
    star = POLARIS_STARS[star_index]
    
    if not consume_item(role, star["item"], 10, db):
        return False, f"需要10个{star['item']}"
    
    if star_index == 2:
        role.max_hp += 500
        role.hp += 500
    elif star_index == 3:
        pass
    
    role.combat_power = calculate_combat_power(role)
    db.commit()
    return True, f"{star['name_zh']}星位强化成功！"


def process_training(role: JingwuRole, db: Session):
    if not role.is_training or not role.training_end:
        return False
    
    now = datetime.utcnow()
    if now < role.training_end:
        return False
    
    duration = (role.training_end - role.training_start).total_seconds() / 3600
    base_exp = int(duration * 500 * (1 + role.level * 0.1))
    
    role.exp += base_exp
    role.is_training = False
    role.training_type = None
    role.training_start = None
    role.training_end = None
    
    leveled_up = False
    while role.exp >= calculate_exp_for_level(role.level):
        role.exp -= calculate_exp_for_level(role.level)
        role.level += 1
        role.potential += 3
        leveled_up = True
    
    if leveled_up:
        stats = calculate_stats(role)
        role.max_hp = stats["max_hp"]
        role.hp = stats["hp"]
        role.max_mp = stats["max_mp"]
        role.mp = stats["mp"]
        role.base_damage = stats["damage"]
        role.base_defense = stats["defense"]
        role.base_speed = stats["speed"]
    
    role.combat_power = calculate_combat_power(role)
    db.commit()
    return True


def start_training(role: JingwuRole, training_type: str = "workshop", hours: int = 4):
    if role.is_training:
        return False
    
    now = datetime.utcnow()
    role.is_training = True
    role.training_type = training_type
    role.training_start = now
    role.training_end = now + timedelta(hours=hours)
    return True


def stop_training(role: JingwuRole, db: Session):
    if not role.is_training:
        return False
    
    now = datetime.utcnow()
    if role.training_start:
        duration = (now - role.training_start).total_seconds() / 3600
        if duration > 0.1:
            base_exp = int(duration * 300 * (1 + role.level * 0.05))
            role.exp += base_exp
    
    role.is_training = False
    role.training_type = None
    role.training_start = None
    role.training_end = None
    role.combat_power = calculate_combat_power(role)
    db.commit()
    return True


def reset_dungeon_attempts(role: JingwuRole, db: Session):
    dungeon = db.query(JingwuDungeon).filter(JingwuDungeon.role_id == role.id).first()
    if not dungeon:
        return
    
    now = datetime.utcnow()
    if (now - dungeon.last_reset).total_seconds() >= 86400:
        dungeon.daily_attempts = dungeon.max_attempts
        dungeon.last_reset = now
        db.commit()


def simulate_battle(attacker: JingwuRole, defender: JingwuRole, db: Session, is_dungeon: bool = False):
    log = []
    rounds = 0
    max_rounds = 20
    
    reset_dungeon_attempts(attacker, db)
    
    atk_hp = attacker.max_hp
    def_hp = defender.max_hp if not is_dungeon else defender.max_hp
    atk_dmg = attacker.base_damage
    def_dmg = defender.base_damage if not is_dungeon else int(defender.base_damage * 0.8)
    atk_def = attacker.base_defense
    def_def = defender.base_defense if not is_dungeon else int(defender.base_defense * 0.8)
    atk_speed = attacker.base_speed
    def_speed = defender.base_speed if not is_dungeon else defender.base_speed - 10
    
    if is_dungeon:
        log.append(f"【副本战斗】{attacker.name}(Lv.{attacker.level}) VS {defender.name}")
    else:
        log.append(f"【比武开始】{attacker.name}(Lv.{attacker.level}) VS {defender.name}(Lv.{defender.level})")
    
    first = attacker if atk_speed >= def_speed else defender
    second = defender if first == attacker else attacker
    
    winner = None
    reward_items = []
    
    while rounds < max_rounds and atk_hp > 0 and def_hp > 0:
        rounds += 1
        
        for actor, target, is_atk in [(first, second, first == attacker), (second, first, first != attacker)]:
            if atk_hp <= 0 or def_hp <= 0:
                break
            
            actor_dmg = atk_dmg if is_atk else def_dmg
            target_def = def_def if is_atk else atk_def
            
            hit = random.randint(1, 100)
            dodge_chance = (defender.base_dodge if is_atk else attacker.base_dodge) / 200
            if hit < dodge_chance * 100:
                log.append(f"回合{rounds}: {actor.name}的攻击被{target.name}闪避了！")
                continue
            
            is_crit = random.randint(1, 100) <= (actor.base_crit)
            base_damage = max(1, actor_dmg - target_def // 2)
            damage = int(base_damage * (1.5 if is_crit else 1) * random.uniform(0.9, 1.1))
            
            if is_atk:
                def_hp -= damage
            else:
                atk_hp -= damage
            
            crit_text = "暴击！" if is_crit else ""
            log.append(f"回合{rounds}: {actor.name}对{target.name}造成{damage}点伤害{crit_text}")
    
    if atk_hp > def_hp:
        winner = attacker
        log.append(f"【战斗结束】{attacker.name}获胜！")
    elif def_hp > atk_hp:
        winner = defender if not is_dungeon else None
        if winner:
            log.append(f"【战斗结束】{defender.name}获胜！")
        else:
            log.append(f"【副本结束】挑战失败...")
    else:
        winner = None
        log.append("【战斗结束】平局！")
    
    reward_silver = 0
    reward_exp = 0
    
    if winner == attacker:
        reward_silver = random.randint(50, 150) if not is_dungeon else random.randint(200, 500)
        reward_exp = random.randint(20, 50) if not is_dungeon else random.randint(100, 300)
        attacker.wins_today += 1
        attacker.wins_week += 1
        attacker.exp += reward_exp
        attacker.user.g_coins += reward_silver
        
        if is_dungeon:
            for stage in DUNGEON_STAGES:
                if stage["boss"] == defender.name:
                    possible_drops = stage["drops"]
                    num_drops = random.randint(1, 3)
                    for _ in range(num_drops):
                        drop = random.choice(possible_drops)
                        reward_items.append(drop)
                    
                    if random.random() < 0.15:
                        reward_items.append("北极星")
                    if stage["level_req"] >= 60 and random.random() < 0.1:
                        reward_items.append("神装图纸")
                    if stage["level_req"] >= 70 and random.random() < 0.1:
                        reward_items.append("神铸模具")
                    break
            
            for item_name in reward_items:
                add_item(attacker, item_name, 1, db=db)
            
            reward_silver += 500
        
        defender.losses_today += 1
    elif winner == defender and not is_dungeon:
        reward_silver = random.randint(20, 50)
        reward_exp = random.randint(5, 15)
        defender.wins_today += 1
        defender.wins_week += 1
        defender.exp += reward_exp
        attacker.losses_today += 1
    
    attacker.hp = max(1, atk_hp)
    attacker.stamina = max(0, attacker.stamina - 5)
    
    for role in [attacker]:
        while role.exp >= calculate_exp_for_level(role.level):
            role.exp -= calculate_exp_for_level(role.level)
            role.level += 1
            role.potential += 3
        role.combat_power = calculate_combat_power(role)
    
    battle_log = BattleLog(
        attacker_id=attacker.id,
        defender_id=defender.id if not is_dungeon else 0,
        winner_id=winner.id if winner else None,
        battle_type="dungeon" if is_dungeon else "pvp",
        rounds=rounds,
        log="\n".join(log),
        reward_silver=reward_silver,
        reward_exp=reward_exp,
        reward_items=json.dumps(reward_items, ensure_ascii=False) if reward_items else None,
    )
    db.add(battle_log)
    db.commit()
    
    return {
        "winner": winner,
        "log": "\n".join(log),
        "rounds": rounds,
        "reward_silver": reward_silver,
        "reward_exp": reward_exp,
        "reward_items": reward_items,
    }


def allocate_point(role: JingwuRole, stat: str, db: Session):
    if role.potential <= 0:
        return False
    
    if stat == "str":
        role.str_point += 1
    elif stat == "con":
        role.con_point += 1
    elif stat == "agi":
        role.agi_point += 1
    elif stat == "def":
        role.def_point += 1
    elif stat == "mag":
        role.mag_point += 1
    else:
        return False
    
    role.potential -= 1
    stats = calculate_stats(role)
    role.max_hp = stats["max_hp"]
    role.max_mp = stats["max_mp"]
    role.base_damage = stats["damage"]
    role.base_defense = stats["defense"]
    role.base_speed = stats["speed"]
    role.base_accuracy = stats["accuracy"]
    role.base_dodge = stats["dodge"]
    role.base_crit = stats["crit"]
    role.combat_power = calculate_combat_power(role)
    db.commit()
    return True


def get_training_time_remaining(role: JingwuRole):
    if not role.is_training or not role.training_end:
        return None
    now = datetime.utcnow()
    remaining = role.training_end - now
    if remaining.total_seconds() <= 0:
        return 0
    hours = int(remaining.total_seconds() // 3600)
    minutes = int((remaining.total_seconds() % 3600) // 60)
    return f"{hours}小时{minutes}分钟"


def equip_item(role: JingwuRole, equipment_id: int, db: Session):
    eq = db.query(JingwuEquipment).filter(
        JingwuEquipment.id == equipment_id,
        JingwuEquipment.owner_id == role.id
    ).first()
    
    if not eq:
        return False
    
    for other in role.equipments:
        if other.slot == eq.slot and other.is_equipped and other.id != eq.id:
            other.is_equipped = False
    
    eq.is_equipped = True
    
    stats = calculate_stats(role)
    role.max_hp = stats["max_hp"]
    role.base_damage = stats["damage"]
    role.base_defense = stats["defense"]
    role.base_speed = stats["speed"]
    role.combat_power = calculate_combat_power(role)
    
    db.commit()
    return True


def use_item(role: JingwuRole, item_id: int, db: Session):
    item = db.query(JingwuItem).filter(JingwuItem.id == item_id, JingwuItem.owner_id == role.id).first()
    if not item:
        return False, "物品不存在"
    
    if item.name == "大力神丸":
        role.stamina = min(role.max_stamina, role.stamina + 30)
        item.quantity -= 1
    elif item.name == "小还丹":
        role.hp = min(role.max_hp, role.hp + 100)
        item.quantity -= 1
    elif item.name == "大还丹":
        role.hp = role.max_hp
        item.quantity -= 1
    elif item.name == "雪参玉蟾丸":
        role.hp = role.max_hp
        role.mp = role.max_mp
        item.quantity -= 1
    else:
        return False, "该物品无法直接使用"
    
    if item.quantity <= 0:
        db.delete(item)
    db.commit()
    return True, "使用成功"
