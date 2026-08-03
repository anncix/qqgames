from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Table, SmallInteger, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


friendship = Table(
    'friendships', Base.metadata,
    Column('id', Integer, primary_key=True, index=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('friend_user_id', Integer, ForeignKey('users.id')),
    Column('status', SmallInteger, default=1),
    Column('group_name', String(50)),
    Column('remark', String(100)),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
)


# ==================== 一、账号与用户主数据 ====================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    status = Column(SmallInteger, default=1)
    register_ip = Column(String(50))
    last_login_ip = Column(String(50))
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    nickname = Column(String(50))
    avatar = Column(String(255), default="👤")
    gender = Column(SmallInteger, default=0)
    birthday = Column(String(20))
    city_code = Column(String(20))
    city = Column(String(50))
    signature = Column(String(255), default="这家伙很懒，什么都没留下...")
    qq_number = Column(String(20))
    vip_level = Column(Integer, default=0)
    
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    popularity = Column(Integer, default=0)
    charm = Column(Integer, default=0)
    visit_count = Column(Integer, default=0)
    
    theme = Column(String(20), default="default")
    allow_visit = Column(Boolean, default=True)
    allow_message = Column(Boolean, default=True)
    show_online = Column(Boolean, default=True)
    language = Column(String(10), default="zh")
    online = Column(Boolean, default=False)

    family_id = Column(Integer, ForeignKey('families.id'), nullable=True)
    family_role = Column(String(20), default="member")

    wallet = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    friends = relationship(
        "User", secondary=friendship,
        primaryjoin=id==friendship.c.user_id,
        secondaryjoin=id==friendship.c.friend_user_id,
        backref="friend_of"
    )
    
    jw_role = relationship("JingwuRole", back_populates="user", uselist=False, cascade="all, delete-orphan")
    farm = relationship("FarmProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    garden = relationship("GardenProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    town = relationship("TownProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sea = relationship("SeaProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    summon = relationship("SummonProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    guestbook = relationship("MessageBoardPost", back_populates="owner", foreign_keys="MessageBoardPost.owner_user_id", cascade="all, delete-orphan")
    visits = relationship("HomepageVisit", back_populates="owner", foreign_keys="HomepageVisit.owner_user_id", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    inventory = relationship("InventoryItem", back_populates="user", cascade="all, delete-orphan")


# ==================== 二、钱包与经济系统 ====================

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", back_populates="wallet")
    
    g_coin = Column(Integer, default=5000)
    gold_coin = Column(Integer, default=0)
    premium_coin = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WalletLog(Base):
    __tablename__ = "wallet_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    currency_type = Column(String(20), nullable=False)
    change_amount = Column(Integer, default=0)
    before_amount = Column(Integer, default=0)
    after_amount = Column(Integer, default=0)
    source_type = Column(String(30))
    source_id = Column(Integer)
    remark = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 三、家园主页与互动 ====================

class HomepageVisit(Base):
    __tablename__ = "homepage_visits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="visits", foreign_keys=[owner_user_id])
    visitor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    visitor_nickname = Column(String(50))
    source_module = Column(String(30))
    action_type = Column(String(30), default="visit")
    created_at = Column(DateTime, default=datetime.utcnow)


class MessageBoardPost(Base):
    __tablename__ = "message_board_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="guestbook", foreign_keys=[owner_user_id])
    author_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_nickname = Column(String(50))
    content = Column(Text, nullable=False)
    reply = Column(Text)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserActionLog(Base):
    __tablename__ = "user_actions_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_key = Column(String(50), nullable=False)
    module_key = Column(String(30))
    value = Column(Integer, default=0)
    payload_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 四、好友系统 ====================

class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    from_nickname = Column(String(50))
    message = Column(String(200))
    status = Column(SmallInteger, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserBlacklist(Base):
    __tablename__ = "user_blacklists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blocked_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 五、家族系统 ====================

class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    owner_user_id = Column(Integer, nullable=False)
    notice = Column(Text)
    description = Column(String(255))
    slogan = Column(String(255))
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    contribution_total = Column(Integer, default=0)
    funds = Column(Integer, default=0)
    member_limit = Column(Integer, default=20)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("User", backref="family", foreign_keys="User.family_id")


class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="member")
    contribution = Column(Integer, default=0)
    today_signin = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=datetime.utcnow)


class FamilySignin(Base):
    __tablename__ = "family_signins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reward_gcoin = Column(Integer, default=0)
    reward_contribution = Column(Integer, default=0)
    signed_at = Column(DateTime, default=datetime.utcnow)


class FamilyChatMessage(Base):
    __tablename__ = "family_chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_nickname = Column(String(50))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 六、论坛系统 ====================

class Forum(Base):
    __tablename__ = "forums"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    category = Column(String(30))
    description = Column(String(255))
    icon = Column(String(50), default="📋")
    sort_order = Column(Integer, default=0)
    status = Column(SmallInteger, default=1)
    post_count = Column(Integer, default=0)


class ForumTopic(Base):
    __tablename__ = "forum_topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    forum_id = Column(Integer, ForeignKey("forums.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user_nickname = Column(String(50))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    view_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    is_elite = Column(Boolean, default=False)
    status = Column(SmallInteger, default=1)
    last_reply_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class ForumPost(Base):
    __tablename__ = "forum_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("forum_topics.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user_nickname = Column(String(50))
    content = Column(Text, nullable=False)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 七、背包与商城 ====================

class InventoryTab(Base):
    __tablename__ = "inventory_tabs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_key = Column(String(30), default="common")
    capacity = Column(Integer, default=50)
    used_count = Column(Integer, default=0)


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="inventory")
    module_key = Column(String(30), default="common")
    item_type = Column(String(30))
    item_code = Column(String(50), nullable=False)
    item_name = Column(String(100))
    quantity = Column(Integer, default=1)
    locked = Column(Boolean, default=False)
    quality = Column(String(20), default="common")
    icon = Column(String(100))
    description = Column(Text)
    extra_json = Column(Text)
    expire_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class ShopItem(Base):
    __tablename__ = "shop_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    module_key = Column(String(30), default="common")
    item_code = Column(String(50), nullable=False)
    item_name = Column(String(100))
    price_currency = Column(String(20), default="g_coin")
    price_amount = Column(Integer, default=0)
    limit_per_day = Column(Integer, default=0)
    status = Column(SmallInteger, default=1)


# ==================== 八、消息、公告、活动、成就、图标 ====================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="notifications")
    type = Column(String(30), default="system")
    module_key = Column(String(30))
    title = Column(String(100))
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    scope_type = Column(String(30), default="all")
    scope_key = Column(String(50))
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(String(30))
    module_key = Column(String(30), default="home")
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    status = Column(SmallInteger, default=1)
    config_json = Column(Text)


class ActivityProgress(Base):
    __tablename__ = "activity_progress"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    progress_value = Column(Integer, default=0)
    progress_json = Column(Text)
    reward_status = Column(SmallInteger, default=0)


class IconDef(Base):
    __tablename__ = "icons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    icon_key = Column(String(50), unique=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(100))
    source_module = Column(String(30))
    description = Column(String(255))
    unlock_rule_json = Column(Text)
    status = Column(SmallInteger, default=1)


class UserIcon(Base):
    __tablename__ = "user_icons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    icon_id = Column(Integer, ForeignKey("icons.id"))
    is_lit = Column(Boolean, default=False)
    is_using = Column(Boolean, default=False)
    lit_at = Column(DateTime)


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(30))
    name = Column(String(50), nullable=False)
    description = Column(String(255))
    icon = Column(String(50))
    points = Column(Integer, default=10)
    rule_json = Column(Text)
    reward_json = Column(Text)


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    progress_value = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)


# ==================== 九、事件总线与排行 ====================

class PlatformEvent(Base):
    __tablename__ = "platform_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    module_key = Column(String(30))
    event_type = Column(String(50), nullable=False)
    event_payload_json = Column(Text)
    processed_status = Column(SmallInteger, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class RankDefinition(Base):
    __tablename__ = "rank_definitions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rank_key = Column(String(50), unique=True)
    name = Column(String(50), nullable=False)
    module_key = Column(String(30))
    period_type = Column(String(20), default="total")
    calc_rule_json = Column(Text)


class RankSnapshot(Base):
    __tablename__ = "rank_snapshots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rank_key = Column(String(50))
    period_value = Column(String(20))
    user_id = Column(Integer, ForeignKey("users.id"))
    user_nickname = Column(String(50))
    score = Column(Integer, default=0)
    rank_no = Column(Integer)
    extra_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 十、精武堂模块 ====================

class JingwuRole(Base):
    __tablename__ = "jingwu_roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", back_populates="jw_role")

    name = Column(String(50), nullable=False)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    gender = Column(String(10), default="male")
    profession = Column(String(20), default="common")

    transferred = Column(Boolean, default=False)
    transfer_path = Column(String(20))
    transfer_name = Column(String(20))

    potential = Column(Integer, default=3)
    str_point = Column(Integer, default=0)
    con_point = Column(Integer, default=0)
    agi_point = Column(Integer, default=0)
    def_point = Column(Integer, default=0)
    mag_point = Column(Integer, default=0)

    hp = Column(Integer, default=100)
    max_hp = Column(Integer, default=100)
    mp = Column(Integer, default=50)
    max_mp = Column(Integer, default=50)
    stamina = Column(Integer, default=100)
    max_stamina = Column(Integer, default=100)

    base_damage = Column(Integer, default=10)
    base_defense = Column(Integer, default=5)
    base_speed = Column(Integer, default=10)
    base_accuracy = Column(Integer, default=100)
    base_dodge = Column(Integer, default=50)
    base_crit = Column(Integer, default=5)
    base_crit_damage = Column(Integer, default=150)

    combat_power = Column(Integer, default=0)
    wins_today = Column(Integer, default=0)
    losses_today = Column(Integer, default=0)
    wins_week = Column(Integer, default=0)

    polaris_level = Column(Integer, default=0)
    polaris_exp = Column(Integer, default=0)

    is_training = Column(Boolean, default=False)
    training_type = Column(String(20))
    training_start = Column(DateTime)
    training_end = Column(DateTime)

    items = relationship("JingwuItem", back_populates="owner", cascade="all, delete-orphan")
    equipments = relationship("JingwuEquipment", back_populates="owner", cascade="all, delete-orphan")
    dungeon = relationship("JingwuDungeon", back_populates="role", uselist=False, cascade="all, delete-orphan")


class JingwuItem(Base):
    __tablename__ = "jingwu_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("jingwu_roles.id"), nullable=False)
    owner = relationship("JingwuRole", back_populates="items")

    item_type = Column(String(20), nullable=False)
    category = Column(String(20), default="other")
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(255))
    quantity = Column(Integer, default=1)
    quality = Column(String(20), default="common")
    is_bound = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class JingwuEquipment(Base):
    __tablename__ = "jingwu_equipments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("jingwu_roles.id"), nullable=False)
    owner = relationship("JingwuRole", back_populates="equipments")

    slot = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    level_required = Column(Integer, default=1)
    quality = Column(String(20), default="common")
    damage = Column(Integer, default=0)
    defense = Column(Integer, default=0)
    hp = Column(Integer, default=0)
    speed = Column(Integer, default=0)
    accuracy = Column(Integer, default=0)
    dodge = Column(Integer, default=0)
    crit = Column(Integer, default=0)
    crit_damage = Column(Integer, default=0)
    enhance_level = Column(Integer, default=0)
    is_equipped = Column(Boolean, default=False)
    gem_slots = Column(Integer, default=0)
    gems = Column(String(255))


class JingwuDungeon(Base):
    __tablename__ = "jingwu_dungeons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("jingwu_roles.id"))
    role = relationship("JingwuRole", back_populates="dungeon")
    dungeon_id = Column(Integer, default=1)
    name = Column(String(50), default="三国副本")
    chapter = Column(Integer, default=1)
    stage = Column(Integer, default=1)
    daily_attempts = Column(Integer, default=3)
    max_attempts = Column(Integer, default=3)
    last_reset = Column(DateTime, default=datetime.utcnow)


class BattleLog(Base):
    __tablename__ = "battle_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    attacker_id = Column(Integer)
    defender_id = Column(Integer)
    winner_id = Column(Integer)
    battle_type = Column(String(20), default="pvp")
    rounds = Column(Integer, default=0)
    log = Column(Text)
    reward_silver = Column(Integer, default=0)
    reward_exp = Column(Integer, default=0)
    reward_items = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 十一、阳光农场模块 ====================

class FarmProfile(Base):
    __tablename__ = "farm_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", back_populates="farm")

    farm_level = Column(Integer, default=1)
    farm_exp = Column(Integer, default=0)
    farm_gold = Column(Integer, default=1000)
    land_count = Column(Integer, default=6)
    barn_level = Column(Integer, default=1)
    weather_seed = Column(String(20), default="sunny")
    created_at = Column(DateTime, default=datetime.utcnow)

    plots = relationship("FarmPlot", back_populates="farm", cascade="all, delete-orphan")
    animals = relationship("FarmAnimal", back_populates="farm", cascade="all, delete-orphan")
    storage = relationship("FarmStorage", back_populates="farm", cascade="all, delete-orphan")


class FarmPlot(Base):
    __tablename__ = "farm_plots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farm_profiles.id"), nullable=False)
    farm = relationship("FarmProfile", back_populates="plots")
    user_id = Column(Integer, ForeignKey("users.id"))
    plot_no = Column(Integer, nullable=False)
    status = Column(String(20), default="idle")
    crop_code = Column(String(50))
    crop_name = Column(String(50))
    stage = Column(String(20))
    planted_at = Column(DateTime)
    ready_at = Column(DateTime)
    water_count = Column(Integer, default=0)
    fertilizer_count = Column(Integer, default=0)
    insect_state = Column(Boolean, default=False)
    weed_state = Column(Boolean, default=False)


class FarmAnimal(Base):
    __tablename__ = "farm_animals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farm_profiles.id"), nullable=False)
    farm = relationship("FarmProfile", back_populates="animals")
    user_id = Column(Integer, ForeignKey("users.id"))
    animal_code = Column(String(50))
    animal_name = Column(String(50))
    status = Column(String(20), default="baby")
    hunger = Column(Integer, default=100)
    health = Column(Integer, default=100)
    ready_at = Column(DateTime)
    production_ready = Column(Boolean, default=False)
    bought_at = Column(DateTime, default=datetime.utcnow)
    shed_index = Column(Integer)


class FarmStorage(Base):
    __tablename__ = "farm_storage"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farm_profiles.id"), nullable=False)
    farm = relationship("FarmProfile", back_populates="storage")
    user_id = Column(Integer, ForeignKey("users.id"))
    item_code = Column(String(50), nullable=False)
    item_name = Column(String(50))
    item_type = Column(String(20), default="crop")
    quantity = Column(Integer, default=0)
    locked = Column(Boolean, default=False)


class FarmFriendAction(Base):
    __tablename__ = "farm_friend_actions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"))
    target_user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String(30), nullable=False)
    target_plot_id = Column(Integer)
    reward_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class FarmVillage(Base):
    __tablename__ = "farm_villages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    member_count = Column(Integer, default=1)
    member_limit = Column(Integer, default=20)
    funds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 十二、美味小镇模块 ====================

class TownProfile(Base):
    __tablename__ = "town_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", back_populates="town")

    restaurant_level = Column(Integer, default=1)
    restaurant_exp = Column(Integer, default=0)
    restaurant_name = Column(String(50), default="我的餐厅")
    star_level = Column(Integer, default=1)
    street_code = Column(String(30), default="chinese")
    oil_amount = Column(Integer, default=100)
    gold = Column(Integer, default=5000)
    seats = Column(Integer, default=4)
    created_at = Column(DateTime, default=datetime.utcnow)

    tables = relationship("TownTable", back_populates="town", cascade="all, delete-orphan")
    recipes = relationship("TownUserRecipe", back_populates="town", cascade="all, delete-orphan")
    ingredients = relationship("TownIngredient", back_populates="town", cascade="all, delete-orphan")


class TownTable(Base):
    __tablename__ = "town_tables"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    town_id = Column(Integer, ForeignKey("town_profiles.id"), nullable=False)
    town = relationship("TownProfile", back_populates="tables")
    user_id = Column(Integer, ForeignKey("users.id"))
    table_no = Column(Integer, nullable=False)
    status = Column(String(20), default="idle")
    waiter_id = Column(Integer)


class TownRecipe(Base):
    __tablename__ = "town_recipes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    street_code = Column(String(30))
    level_required = Column(Integer, default=1)
    quality_type = Column(String(20), default="normal")
    ingredient_json = Column(Text)
    oil_cost = Column(Integer, default=1)
    gold_income = Column(Integer, default=10)
    exp_income = Column(Integer, default=5)


class TownUserRecipe(Base):
    __tablename__ = "town_user_recipes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    town_id = Column(Integer, ForeignKey("town_profiles.id"), nullable=False)
    town = relationship("TownProfile", back_populates="recipes")
    user_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer, ForeignKey("town_recipes.id"))
    quality_level = Column(String(20), default="normal")
    learned_at = Column(DateTime, default=datetime.utcnow)


class TownIngredient(Base):
    __tablename__ = "town_ingredients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    town_id = Column(Integer, ForeignKey("town_profiles.id"), nullable=False)
    town = relationship("TownProfile", back_populates="ingredients")
    user_id = Column(Integer, ForeignKey("users.id"))
    ingredient_code = Column(String(50), nullable=False)
    ingredient_name = Column(String(50))
    quantity = Column(Integer, default=0)
    locked = Column(Boolean, default=False)


class TownFriendAction(Base):
    __tablename__ = "town_friend_actions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"))
    target_user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String(30), nullable=False)
    reward_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class TownWaiter(Base):
    __tablename__ = "town_waiters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    town_id = Column(Integer, ForeignKey("town_profiles.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    friend_user_id = Column(Integer, ForeignKey("users.id"))
    friend_nickname = Column(String(50))
    status = Column(String(20), default="on")
    bound_table_count = Column(Integer, default=0)
    salary = Column(Integer, default=100)
    hired_at = Column(DateTime, default=datetime.utcnow)


class TownOrder(Base):
    __tablename__ = "town_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    town_id = Column(Integer, ForeignKey("town_profiles.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    table_id = Column(Integer, ForeignKey("town_tables.id"))
    customer_type = Column(String(20), default="normal")
    recipe_id = Column(Integer, ForeignKey("town_recipes.id"))
    recipe_name = Column(String(100))
    status = Column(String(20), default="waiting")
    reward_gold = Column(Integer, default=0)
    reward_exp = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


# ==================== 十三、魔法花园模块 ====================

class GardenProfile(Base):
    __tablename__ = "garden_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", back_populates="garden")

    garden_level = Column(Integer, default=1)
    garden_exp = Column(Integer, default=0)
    gold = Column(Integer, default=500)
    plot_count = Column(Integer, default=6)
    album_lit_count = Column(Integer, default=0)
    reputation = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    plots = relationship("GardenPlot", back_populates="garden", cascade="all, delete-orphan")
    flowers = relationship("GardenUserFlower", back_populates="garden", cascade="all, delete-orphan")


class GardenPlot(Base):
    __tablename__ = "garden_plots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    garden_id = Column(Integer, ForeignKey("garden_profiles.id"), nullable=False)
    garden = relationship("GardenProfile", back_populates="plots")
    user_id = Column(Integer, ForeignKey("users.id"))
    plot_no = Column(Integer, nullable=False)
    seed_code = Column(String(50))
    flower_name = Column(String(50))
    stage = Column(String(20))
    color = Column(String(20))
    planted_at = Column(DateTime)
    ready_at = Column(DateTime)
    watered = Column(Boolean, default=False)
    weeded = Column(Boolean, default=False)
    insect_state = Column(Boolean, default=False)


class GardenFlower(Base):
    __tablename__ = "garden_flowers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    flower_code = Column(String(50), unique=True)
    seed_code = Column(String(50))
    name = Column(String(50), nullable=False)
    rarity = Column(String(20), default="common")
    base_colors_json = Column(Text)
    price = Column(Integer, default=10)
    exp_gain = Column(Integer, default=5)
    grow_time = Column(Integer, default=300)
    album_group = Column(String(30))


class GardenUserFlower(Base):
    __tablename__ = "garden_user_flowers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    garden_id = Column(Integer, ForeignKey("garden_profiles.id"), nullable=False)
    garden = relationship("GardenProfile", back_populates="flowers")
    user_id = Column(Integer, ForeignKey("users.id"))
    flower_code = Column(String(50), nullable=False)
    flower_name = Column(String(50))
    color = Column(String(20))
    quantity = Column(Integer, default=0)
    storage_type = Column(String(20), default="flower")


class GardenAlbumEntry(Base):
    __tablename__ = "garden_album_entries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    flower_code = Column(String(50))
    flower_name = Column(String(50))
    color = Column(String(20))
    category = Column(String(30))
    sort_order = Column(Integer, default=0)


class GardenUserAlbum(Base):
    __tablename__ = "garden_user_album"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    album_entry_id = Column(Integer, ForeignKey("garden_album_entries.id"))
    is_lit = Column(Boolean, default=False)
    lit_at = Column(DateTime)


class GardenFriendAction(Base):
    __tablename__ = "garden_friend_actions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"))
    target_user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String(30), nullable=False)
    flower_code = Column(String(50))
    reward_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class GardenComposeRule(Base):
    __tablename__ = "garden_compose_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    target_seed_code = Column(String(50), nullable=False)
    target_flower_name = Column(String(50))
    cost_json = Column(Text, nullable=False)
    success_rate = Column(Numeric(5, 2), default=1.00)
    gold_cost = Column(Integer, default=0)


# ==================== 十四、纵横四海模块 ====================

class SeaProfile(Base):
    __tablename__ = "sea_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", back_populates="sea")

    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    current_city_code = Column(String(50), default="quanzhou")
    silver_coin = Column(Integer, default=1000)
    power = Column(Integer, default=100)
    max_power = Column(Integer, default=100)
    reputation = Column(Integer, default=0)
    ship_name = Column(String(50), default="我的船")
    ship_level = Column(Integer, default=1)
    ship_hp = Column(Integer, default=100)
    ship_max_hp = Column(Integer, default=100)
    ship_damage = Column(Integer, default=10)
    ship_defense = Column(Integer, default=5)
    ship_capacity = Column(Integer, default=50)
    supplies = Column(Integer, default=100)
    max_supplies = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("SeaUserTask", back_populates="sea", cascade="all, delete-orphan")


class SeaCity(Base):
    __tablename__ = "sea_cities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    city_code = Column(String(50), unique=True)
    name = Column(String(50), nullable=False)
    region = Column(String(30))
    level_range = Column(String(20))
    description = Column(String(255))
    unlock_rule_json = Column(Text)


class SeaUserCity(Base):
    __tablename__ = "sea_user_cities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    city_id = Column(Integer, ForeignKey("sea_cities.id"))
    unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime)


class SeaRoute(Base):
    __tablename__ = "sea_routes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    from_city_code = Column(String(50))
    to_city_code = Column(String(50))
    danger_level = Column(Integer, default=1)
    travel_time = Column(Integer, default=60)
    event_pool_json = Column(Text)


class SeaTask(Base):
    __tablename__ = "sea_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_type = Column(String(30), default="main")
    title = Column(String(100), nullable=False)
    description = Column(Text)
    city_code = Column(String(50))
    level_required = Column(Integer, default=1)
    objective_json = Column(Text)
    reward_json = Column(Text)


class SeaUserTask(Base):
    __tablename__ = "sea_user_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sea_id = Column(Integer, ForeignKey("sea_profiles.id"), nullable=False)
    sea = relationship("SeaProfile", back_populates="tasks")
    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("sea_tasks.id"))
    status = Column(String(20), default="available")
    progress_json = Column(Text)
    accepted_at = Column(DateTime)
    completed_at = Column(DateTime)


class SeaEvent(Base):
    __tablename__ = "sea_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    route_id = Column(Integer)
    event_type = Column(String(30))
    result_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class SeaBattle(Base):
    __tablename__ = "sea_battles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    enemy_type = Column(String(30))
    enemy_name = Column(String(50))
    battle_result = Column(String(10))
    reward_json = Column(Text)
    log = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class SeaEquipment(Base):
    __tablename__ = "sea_equipments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equip_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    slot_type = Column(String(20))
    rarity = Column(String(20), default="common")
    level_required = Column(Integer, default=1)
    base_attr_json = Column(Text)
    icon = Column(String(100))
    price = Column(Integer, default=0)


class SeaUserEquipment(Base):
    __tablename__ = "sea_user_equipments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    equip_id = Column(Integer, ForeignKey("sea_equipments.id"))
    enhance_level = Column(Integer, default=0)
    gem_json = Column(Text)
    equipped = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 十五、家园主页配置 ====================

class UserHomepage(Base):
    __tablename__ = "user_homepages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    skin_id = Column(Integer, default=1)
    background_id = Column(Integer, default=1)
    music_id = Column(Integer)
    layout_json = Column(Text)
    visit_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    guestbook_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HomepageModule(Base):
    __tablename__ = "homepage_modules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    module_key = Column(String(50), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    type = Column(String(20), default="display")
    default_enabled = Column(Boolean, default=True)
    config_schema = Column(Text)
    icon = Column(String(50))


class UserHomepageModule(Base):
    __tablename__ = "user_homepage_modules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_key = Column(String(50), nullable=False)
    position = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    config_json = Column(Text)


# ==================== 十六、聊天室 ====================

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_type = Column(String(20), default="public")
    room_key = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user_nickname = Column(String(50))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 十七、同城系统 ====================

class City(Base):
    __tablename__ = "cities"

    code = Column(String(20), primary_key=True)
    name = Column(String(50), nullable=False)
    province = Column(String(50))
    status = Column(SmallInteger, default=1)


class CityFeed(Base):
    __tablename__ = "city_feeds"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    city_code = Column(String(20), ForeignKey("cities.code"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user_nickname = Column(String(50))
    content = Column(Text, nullable=False)
    type = Column(String(20), default="mood")
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 二十一、精武堂补充 - 帮派系统 ====================

class JingwuGang(Base):
    __tablename__ = "jingwu_gangs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    leader_id = Column(Integer)
    leader_name = Column(String(50))
    notice = Column(Text)
    description = Column(String(255))
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    funds = Column(Integer, default=0)
    member_count = Column(Integer, default=1)
    member_limit = Column(Integer, default=30)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class JingwuGangMember(Base):
    __tablename__ = "jingwu_gang_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    gang_id = Column(Integer, ForeignKey("jingwu_gangs.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("jingwu_roles.id"))
    role_name = Column(String(20), default="member")
    nickname = Column(String(50))
    contribution = Column(Integer, default=0)
    position = Column(String(20), default="member")
    joined_at = Column(DateTime, default=datetime.utcnow)


class JingwuGangSkill(Base):
    __tablename__ = "jingwu_gang_skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    gang_id = Column(Integer, ForeignKey("jingwu_gangs.id"))
    skill_name = Column(String(50))
    skill_type = Column(String(20))
    level = Column(Integer, default=1)
    max_level = Column(Integer, default=10)
    effect_json = Column(Text)


# ==================== 二十二、武魂、法宝等精武堂扩展 ====================

class JingwuWuhun(Base):
    __tablename__ = "jingwu_wuhun"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("jingwu_roles.id"), unique=True)
    wuhun_type = Column(String(20), default="green")
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    str_bonus = Column(Integer, default=0)
    con_bonus = Column(Integer, default=0)
    agi_bonus = Column(Integer, default=0)
    def_bonus = Column(Integer, default=0)
    mag_bonus = Column(Integer, default=0)


class JingwuFabao(Base):
    __tablename__ = "jingwu_fabao"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("jingwu_roles.id"))
    fabao_code = Column(String(50))
    name = Column(String(100))
    quality = Column(String(20), default="common")
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    skill_name = Column(String(50))
    skill_desc = Column(Text)
    is_equipped = Column(Boolean, default=False)
    attr_json = Column(Text)


class JingwuForgeLog(Base):
    __tablename__ = "jingwu_forge_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("jingwu_roles.id"))
    equip_id = Column(Integer)
    equip_name = Column(String(100))
    forge_type = Column(String(20))
    success = Column(Boolean, default=False)
    material_json = Column(Text)
    result_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 二十三、纵横四海扩展系统 ====================

class SeaPet(Base):
    __tablename__ = "sea_pets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pet_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    category = Column(String(20), default="normal")
    rarity = Column(String(20), default="common")
    level_required = Column(Integer, default=1)
    base_hp = Column(Integer, default=100)
    base_atk = Column(Integer, default=10)
    base_def = Column(Integer, default=5)
    base_agi = Column(Integer, default=10)
    skill_pool_json = Column(Text)
    icon = Column(String(100))
    description = Column(Text)


class SeaUserPet(Base):
    __tablename__ = "sea_user_pets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    pet_id = Column(Integer, ForeignKey("sea_pets.id"))
    nickname = Column(String(50))
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    hp = Column(Integer, default=100)
    atk = Column(Integer, default=10)
    def_ = Column("def", Integer, default=5)
    agi = Column(Integer, default=10)
    skills_json = Column(Text)
    is_battling = Column(Boolean, default=False)
    intimacy = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class SeaMount(Base):
    __tablename__ = "sea_mounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mount_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    level_required = Column(Integer, default=80)
    rarity = Column(String(20), default="common")
    speed_bonus = Column(Integer, default=0)
    hp_bonus = Column(Integer, default=0)
    atk_bonus = Column(Integer, default=0)
    def_bonus = Column(Integer, default=0)
    icon = Column(String(100))
    description = Column(Text)


class SeaUserMount(Base):
    __tablename__ = "sea_user_mounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    mount_id = Column(Integer, ForeignKey("sea_mounts.id"))
    level = Column(Integer, default=1)
    is_riding = Column(Boolean, default=False)
    riding_skill_level = Column(Integer, default=1)
    obtained_at = Column(DateTime, default=datetime.utcnow)


class SeaWing(Base):
    __tablename__ = "sea_wings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    wing_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    level_required = Column(Integer, default=100)
    rarity = Column(String(20), default="common")
    hp_bonus = Column(Integer, default=0)
    atk_bonus = Column(Integer, default=0)
    def_bonus = Column(Integer, default=0)
    vampire_rate = Column(Integer, default=0)
    combo_rate = Column(Integer, default=0)
    iron_wall_rate = Column(Integer, default=0)
    icon = Column(String(100))


class SeaUserWing(Base):
    __tablename__ = "sea_user_wings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    wing_id = Column(Integer, ForeignKey("sea_wings.id"))
    level = Column(Integer, default=1)
    is_equipped = Column(Boolean, default=False)
    wing_skill_level = Column(Integer, default=1)
    obtained_at = Column(DateTime, default=datetime.utcnow)


class SeaFollower(Base):
    __tablename__ = "sea_followers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    follower_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    quality = Column(String(20), default="normal")
    level_required = Column(Integer, default=50)
    base_hp = Column(Integer, default=100)
    base_atk = Column(Integer, default=15)
    base_def = Column(Integer, default=10)
    talent_skill = Column(String(100))
    talent_desc = Column(Text)
    icon = Column(String(100))
    description = Column(Text)


class SeaUserFollower(Base):
    __tablename__ = "sea_user_followers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    follower_id = Column(Integer, ForeignKey("sea_followers.id"))
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    quality = Column(String(20), default="normal")
    hp = Column(Integer, default=100)
    atk = Column(Integer, default=15)
    def_ = Column("def", Integer, default=10)
    is_battling = Column(Boolean, default=False)
    inherited = Column(Boolean, default=False)
    cultivate_json = Column(Text)
    obtained_at = Column(DateTime, default=datetime.utcnow)


class SeaGem(Base):
    __tablename__ = "sea_gems"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    gem_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    color = Column(String(20))
    slot_type = Column(String(20))
    rarity = Column(String(20), default="common")
    level = Column(Integer, default=1)
    atk_bonus = Column(Integer, default=0)
    def_bonus = Column(Integer, default=0)
    hp_bonus = Column(Integer, default=0)
    agi_bonus = Column(Integer, default=0)
    icon = Column(String(100))


class SeaUserGem(Base):
    __tablename__ = "sea_user_gems"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    gem_id = Column(Integer, ForeignKey("sea_gems.id"))
    level = Column(Integer, default=1)
    quantity = Column(Integer, default=1)
    inlaid_equip_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class SeaCard(Base):
    __tablename__ = "sea_cards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    card_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    quality = Column(String(20), default="common")
    star_level = Column(Integer, default=1)
    slot_type = Column(String(20))
    monster_source = Column(String(100))
    atk_bonus = Column(Integer, default=0)
    def_bonus = Column(Integer, default=0)
    hp_bonus = Column(Integer, default=0)
    special_effect = Column(Text)
    icon = Column(String(100))


class SeaUserCard(Base):
    __tablename__ = "sea_user_cards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    card_id = Column(Integer, ForeignKey("sea_cards.id"))
    enhance_level = Column(Integer, default=0)
    is_equipped = Column(Boolean, default=False)
    equipped_slot = Column(String(20))
    obtained_at = Column(DateTime, default=datetime.utcnow)


class SeaStigmata(Base):
    __tablename__ = "sea_stigmata"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    stigmata_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    category = Column(String(20))
    quality = Column(String(20), default="common")
    level_required = Column(Integer, default=1)
    base_atk = Column(Integer, default=0)
    base_def = Column(Integer, default=0)
    base_hp = Column(Integer, default=0)
    icon = Column(String(100))
    description = Column(Text)


class SeaUserStigmata(Base):
    __tablename__ = "sea_user_stigmata"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stigmata_id = Column(Integer, ForeignKey("sea_stigmata.id"))
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    is_equipped = Column(Boolean, default=False)
    equipped_slot = Column(Integer)
    devour_exp = Column(Integer, default=0)
    obtained_at = Column(DateTime, default=datetime.utcnow)


class SeaHideout(Base):
    __tablename__ = "sea_hideouts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    farm_level = Column(Integer, default=1)
    training_room_level = Column(Integer, default=1)
    farm_plots_count = Column(Integer, default=4)
    last_farm_harvest = Column(DateTime)
    last_training_reward = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class SeaHideoutPlot(Base):
    __tablename__ = "sea_hideout_plots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hideout_id = Column(Integer, ForeignKey("sea_hideouts.id"))
    plot_no = Column(Integer, nullable=False)
    crop_code = Column(String(50))
    crop_name = Column(String(50))
    planted_at = Column(DateTime)
    ready_at = Column(DateTime)
    status = Column(String(20), default="idle")
    silver_reward = Column(Integer, default=0)


class SeaTrainingRoom(Base):
    __tablename__ = "sea_training_rooms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hideout_id = Column(Integer, ForeignKey("sea_hideouts.id"))
    doll_count = Column(Integer, default=1)
    exp_per_hour = Column(Integer, default=100)
    is_training = Column(Boolean, default=False)
    training_start = Column(DateTime)
    accumulated_exp = Column(Integer, default=0)


class SeaGoods(Base):
    __tablename__ = "sea_goods"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    goods_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    category = Column(String(20))
    buy_price = Column(Integer, default=0)
    sell_price = Column(Integer, default=0)
    level_required = Column(Integer, default=1)
    description = Column(Text)
    icon = Column(String(100))


class SeaUserGoods(Base):
    __tablename__ = "sea_user_goods"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goods_code = Column(String(50))
    goods_name = Column(String(100))
    quantity = Column(Integer, default=1)
    category = Column(String(20))
    locked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 二十四、召唤之王模块 ====================

class SummonProfile(Base):
    __tablename__ = "summon_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", back_populates="summon")

    summoner_name = Column(String(50))
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    vitality = Column(Integer, default=100)
    max_vitality = Column(Integer, default=100)
    copper_coin = Column(Integer, default=1000)
    yuanbao = Column(Integer, default=0)
    prestige = Column(Integer, default=0)
    arena_rank = Column(Integer, default=0)
    arena_tier = Column(String(20), default="huang")
    alliance_id = Column(Integer, ForeignKey("summon_alliances.id"))
    master_user_id = Column(Integer)
    apprentice_count = Column(Integer, default=0)
    taoli_value = Column(Integer, default=0)
    catch_ball_normal = Column(Integer, default=20)
    catch_ball_strong = Column(Integer, default=5)
    catch_ball_super = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    beasts = relationship("SummonUserBeast", back_populates="profile", cascade="all, delete-orphan")


class SummonMap(Base):
    __tablename__ = "summon_maps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    map_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    level_min = Column(Integer, default=1)
    level_max = Column(Integer, default=100)
    beast_pool_json = Column(Text)
    drop_json = Column(Text)
    description = Column(Text)
    vitality_cost = Column(Integer, default=1)


class SummonBeast(Base):
    __tablename__ = "summon_beasts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    beast_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    race_type = Column(String(20), default="beast")
    map_level_min = Column(Integer, default=1)
    rarity = Column(String(20), default="common")
    base_hp = Column(Integer, default=100)
    base_patk = Column(Integer, default=15)
    base_matk = Column(Integer, default=10)
    base_pdef = Column(Integer, default=10)
    base_mdef = Column(Integer, default=8)
    base_speed = Column(Integer, default=10)
    growth_min = Column(Integer, default=1)
    growth_max = Column(Integer, default=5)
    skill_pool_json = Column(Text)
    personality_pool_json = Column(Text)
    icon = Column(String(100))
    description = Column(Text)
    catch_rate = Column(Integer, default=50)


class SummonUserBeast(Base):
    __tablename__ = "summon_user_beasts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("summon_profiles.id"), nullable=False)
    profile = relationship("SummonProfile", back_populates="beasts")
    user_id = Column(Integer, ForeignKey("users.id"))
    beast_id = Column(Integer, ForeignKey("summon_beasts.id"))

    nickname = Column(String(50))
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    growth_star = Column(Integer, default=1)
    personality = Column(String(20), default="brave")
    quality = Column(String(20), default="normal")

    hp = Column(Integer, default=100)
    max_hp = Column(Integer, default=100)
    patk = Column(Integer, default=15)
    matk = Column(Integer, default=10)
    pdef = Column(Integer, default=10)
    mdef = Column(Integer, default=8)
    speed = Column(Integer, default=10)

    status = Column(String(20), default="rest")
    awakened = Column(Boolean, default=False)
    rebirth_count = Column(Integer, default=0)
    obtained_at = Column(DateTime, default=datetime.utcnow)

    skills = relationship("SummonUserBeastSkill", back_populates="beast", cascade="all, delete-orphan")
    bones = relationship("SummonUserBone", back_populates="beast", cascade="all, delete-orphan")
    souls = relationship("SummonUserSoul", back_populates="beast", cascade="all, delete-orphan")
    spirits = relationship("SummonUserSpirit", back_populates="beast", cascade="all, delete-orphan")


class SummonSkill(Base):
    __tablename__ = "summon_skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    skill_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    skill_type = Column(String(20), default="active")
    category = Column(String(20), default="patk")
    damage_formula = Column(String(100))
    base_damage = Column(Integer, default=10)
    trigger_rate = Column(Integer, default=100)
    mp_cost = Column(Integer, default=0)
    cooldown = Column(Integer, default=0)
    description = Column(Text)
    icon = Column(String(100))


class SummonUserBeastSkill(Base):
    __tablename__ = "summon_user_beast_skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    beast_id = Column(Integer, ForeignKey("summon_user_beasts.id"), nullable=False)
    beast = relationship("SummonUserBeast", back_populates="skills")
    skill_id = Column(Integer, ForeignKey("summon_skills.id"))
    skill_level = Column(Integer, default=1)
    slot_position = Column(Integer, default=0)
    learned_at = Column(DateTime, default=datetime.utcnow)


class SummonCatchLog(Base):
    __tablename__ = "summon_catch_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    map_id = Column(Integer, ForeignKey("summon_maps.id"))
    beast_id = Column(Integer, ForeignKey("summon_beasts.id"))
    beast_name = Column(String(100))
    ball_type = Column(String(20), default="normal")
    success = Column(Boolean, default=False)
    user_beast_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class SummonBone(Base):
    __tablename__ = "summon_bones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bone_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    slot_type = Column(String(20), nullable=False)
    quality = Column(String(20), default="common")
    level_required = Column(Integer, default=1)
    hp_bonus = Column(Integer, default=0)
    patk_bonus = Column(Integer, default=0)
    matk_bonus = Column(Integer, default=0)
    pdef_bonus = Column(Integer, default=0)
    mdef_bonus = Column(Integer, default=0)
    speed_bonus = Column(Integer, default=0)
    icon = Column(String(100))


class SummonUserBone(Base):
    __tablename__ = "summon_user_bones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    beast_id = Column(Integer, ForeignKey("summon_user_beasts.id"), nullable=False)
    beast = relationship("SummonUserBeast", back_populates="bones")
    user_id = Column(Integer, ForeignKey("users.id"))
    bone_id = Column(Integer, ForeignKey("summon_bones.id"))
    slot_type = Column(String(20), nullable=False)
    quality = Column(String(20), default="common")
    enhance_level = Column(Integer, default=0)
    advance_level = Column(Integer, default=0)
    hp_bonus = Column(Integer, default=0)
    patk_bonus = Column(Integer, default=0)
    matk_bonus = Column(Integer, default=0)
    pdef_bonus = Column(Integer, default=0)
    mdef_bonus = Column(Integer, default=0)
    speed_bonus = Column(Integer, default=0)
    equipped = Column(Boolean, default=True)


class SummonSoul(Base):
    __tablename__ = "summon_souls"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    soul_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    quality = Column(String(20), default="waste")
    category = Column(String(20))
    fixed_hp = Column(Integer, default=0)
    fixed_patk = Column(Integer, default=0)
    fixed_matk = Column(Integer, default=0)
    fixed_pdef = Column(Integer, default=0)
    fixed_mdef = Column(Integer, default=0)
    fixed_speed = Column(Integer, default=0)
    percent_hp = Column(Integer, default=0)
    percent_patk = Column(Integer, default=0)
    percent_matk = Column(Integer, default=0)
    percent_pdef = Column(Integer, default=0)
    percent_mdef = Column(Integer, default=0)
    percent_speed = Column(Integer, default=0)
    icon = Column(String(100))


class SummonUserSoul(Base):
    __tablename__ = "summon_user_souls"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    beast_id = Column(Integer, ForeignKey("summon_user_beasts.id"), nullable=False)
    beast = relationship("SummonUserBeast", back_populates="souls")
    user_id = Column(Integer, ForeignKey("users.id"))
    soul_id = Column(Integer, ForeignKey("summon_souls.id"))
    level = Column(Integer, default=1)
    soul_power = Column(Integer, default=0)
    equipped = Column(Boolean, default=False)
    slot_position = Column(Integer, default=0)
    obtained_at = Column(DateTime, default=datetime.utcnow)


class SummonSoulHuntLog(Base):
    __tablename__ = "summon_soul_hunt_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    hunter_level = Column(Integer, default=1)
    cost_copper = Column(Integer, default=0)
    cost_yuanbao = Column(Integer, default=0)
    soul_id = Column(Integer, ForeignKey("summon_souls.id"))
    soul_quality = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)


class SummonSpirit(Base):
    __tablename__ = "summon_spirits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    spirit_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    element_type = Column(String(20), nullable=False)
    quality = Column(String(20), default="common")
    attr_pool_json = Column(Text)
    icon = Column(String(100))


class SummonUserSpirit(Base):
    __tablename__ = "summon_user_spirits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    beast_id = Column(Integer, ForeignKey("summon_user_beasts.id"), nullable=False)
    beast = relationship("SummonUserBeast", back_populates="spirits")
    user_id = Column(Integer, ForeignKey("users.id"))
    spirit_id = Column(Integer, ForeignKey("summon_spirits.id"))
    element_type = Column(String(20), nullable=False)
    quality = Column(String(20), default="common")
    current_attr_json = Column(Text)
    wash_count = Column(Integer, default=0)
    locked = Column(Boolean, default=False)
    equipped = Column(Boolean, default=True)
    obtained_at = Column(DateTime, default=datetime.utcnow)


class SummonArenaMatch(Base):
    __tablename__ = "summon_arena_matches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    attacker_id = Column(Integer, ForeignKey("users.id"))
    defender_id = Column(Integer, ForeignKey("users.id"))
    attacker_nickname = Column(String(50))
    defender_nickname = Column(String(50))
    tier = Column(String(20), default="huang")
    result = Column(String(10))
    attacker_rank_change = Column(Integer, default=0)
    defender_rank_change = Column(Integer, default=0)
    prestige_change = Column(Integer, default=0)
    battle_log = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class SummonBattlefield(Base):
    __tablename__ = "summon_battlefields"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    battlefield_code = Column(String(50), unique=True)
    name = Column(String(100), nullable=False)
    level_min = Column(Integer, default=1)
    level_max = Column(Integer, default=100)
    open_time_start = Column(String(10), default="06:00")
    open_time_end = Column(String(10), default="24:00")
    camp_a_name = Column(String(50), default="猛虎营")
    camp_b_name = Column(String(50), default="飞鹤寨")
    prestige_reward_win = Column(Integer, default=50)
    prestige_reward_lose = Column(Integer, default=20)
    exp_reward = Column(Integer, default=100)


class SummonBattlefieldRecord(Base):
    __tablename__ = "summon_battlefield_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    battlefield_id = Column(Integer, ForeignKey("summon_battlefields.id"))
    camp = Column(String(10))
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    result = Column(String(10))
    prestige_reward = Column(Integer, default=0)
    exp_reward = Column(Integer, default=0)
    copper_reward = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class SummonAlliance(Base):
    __tablename__ = "summon_alliances"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    leader_user_id = Column(Integer)
    leader_nickname = Column(String(50))
    notice = Column(Text)
    description = Column(String(255))
    level = Column(Integer, default=1)
    funds = Column(Integer, default=0)
    contribution_total = Column(Integer, default=0)
    member_count = Column(Integer, default=1)
    member_limit = Column(Integer, default=30)
    skill_level_json = Column(Text)
    storage_capacity = Column(Integer, default=20)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class SummonAllianceMember(Base):
    __tablename__ = "summon_alliance_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alliance_id = Column(Integer, ForeignKey("summon_alliances.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user_nickname = Column(String(50))
    role = Column(String(20), default="member")
    contribution = Column(Integer, default=0)
    total_donation = Column(Integer, default=0)
    joined_at = Column(DateTime, default=datetime.utcnow)


class SummonAllianceDonationLog(Base):
    __tablename__ = "summon_alliance_donation_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alliance_id = Column(Integer, ForeignKey("summon_alliances.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user_nickname = Column(String(50))
    donation_type = Column(String(20))
    amount = Column(Integer, default=0)
    contribution_reward = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class SummonMasterApprentice(Base):
    __tablename__ = "summon_master_apprentice"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    master_user_id = Column(Integer, ForeignKey("users.id"))
    master_nickname = Column(String(50))
    apprentice_user_id = Column(Integer, ForeignKey("users.id"))
    apprentice_nickname = Column(String(50))
    status = Column(String(20), default="active")
    vitality_today = Column(Boolean, default=False)
    graduated = Column(Boolean, default=False)
    graduated_at = Column(DateTime)
    taoli_reward_taken = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)