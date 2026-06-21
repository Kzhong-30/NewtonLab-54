#!/usr/bin/env python3
import sys
import os
from datetime import date, time, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import (
    User, UserRole, Gender,
    Script, ScriptType, DifficultyLevel,
    Character,
    Game, GameStatus, AssignmentMethod,
    GameParticipant,
    DMProfile, DMSchedule,
    StoreProfile,
    Review,
    CommunityPost, PostType,
    Comment
)
import bcrypt
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    print("=" * 50)
    print("剧本杀平台 - 数据库初始化")
    print("=" * 50)
    print()

    print("[1/7] 创建测试用户...")
    if db.query(User).count() == 0:
        users_data = [
            {"username": "admin", "email": "admin@scriptkill.com", "password": "admin123", "nickname": "系统管理员", "role": UserRole.ADMIN, "gender": Gender.MALE, "phone": "13800000001", "bio": "平台管理员"},
            {"username": "dm_user", "email": "dm@scriptkill.com", "password": "dm123456", "nickname": "资深DM小明", "role": UserRole.DM, "gender": Gender.MALE, "phone": "13800000002", "bio": "5年剧本杀DM经验"},
            {"username": "store_user", "email": "store@scriptkill.com", "password": "store123", "nickname": "迷雾剧本馆", "role": UserRole.STORE_OWNER, "gender": Gender.FEMALE, "phone": "13800000003", "bio": "迷雾剧本馆店主"},
            {"username": "player1", "email": "player1@scriptkill.com", "password": "player123", "nickname": "剧本爱好者", "role": UserRole.PLAYER, "gender": Gender.MALE, "phone": "13800000004", "bio": "喜欢推理本"},
            {"username": "player2", "email": "player2@scriptkill.com", "password": "player123", "nickname": "情感水龙头", "role": UserRole.PLAYER, "gender": Gender.FEMALE, "phone": "13800000005", "bio": "最爱情感本"}
        ]
        for user_data in users_data:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                nickname=user_data["nickname"],
                role=user_data["role"],
                gender=user_data["gender"],
                phone=user_data["phone"],
                bio=user_data["bio"],
                is_active=True,
                is_verified=True
            )
            db.add(user)
        db.flush()
        print(f"  ✓ 创建了 {len(users_data)} 个测试用户")
    else:
        print(f"  ✓ 已存在用户，跳过创建")
    print()

    print("[2/7] 创建 DM 和店家资料...")
    dm_user = db.query(User).filter(User.username == "dm_user").first()
    store_user = db.query(User).filter(User.username == "store_user").first()
    
    if dm_user and not dm_user.dm_profile:
        dm_profile = DMProfile(
            user_id=dm_user.id,
            real_name="张三",
            experience_years=5,
            description="专业DM，控场能力强",
            good_script_types=["emotion", "reasoning"],
            average_rating=4.8,
            total_games=156,
            is_approved=True
        )
        db.add(dm_profile)
        print("  ✓ 创建 DM 资料")
    
    if store_user and not store_user.store_profile:
        store_profile = StoreProfile(
            user_id=store_user.id,
            store_name="迷雾剧本杀体验馆",
            store_address="北京市朝阳区建国路88号",
            store_phone="010-12345678",
            description="专业剧本杀门店",
            average_rating=4.9,
            total_games=328,
            is_approved=True
        )
        db.add(store_profile)
        print("  ✓ 创建店家资料")
    db.flush()
    print()

    print("[3/7] 创建剧本和角色...")
    if db.query(Script).count() == 0:
        store_profile = db.query(StoreProfile).first()
        scripts_data = [
            {
                "title": "年轮", "description": "经典硬核推理本",
                "script_type": ScriptType.REASONING, "difficulty": DifficultyLevel.HARD,
                "min_players": 5, "max_players": 5, "estimated_duration": 240,
                "price": 128.0, "author": "王鑫", "publisher": "天津剧盟",
                "publish_year": 2019, "average_rating": 4.9, "total_reviews": 128,
                "is_approved": True,
                "characters": [
                    {"name": "姚波", "gender": Gender.MALE, "age": 33, "description": "身形消瘦"},
                    {"name": "刘伯钊", "gender": Gender.MALE, "age": 45, "description": "表情严肃"},
                    {"name": "王小冉", "gender": Gender.FEMALE, "age": 27, "description": "眼神忧郁"},
                    {"name": "陈烁", "gender": Gender.MALE, "age": 27, "description": "身材健硕"},
                    {"name": "袁本", "gender": Gender.FEMALE, "age": 26, "description": "眼神坚毅", "is_lead": True}
                ]
            },
            {
                "title": "你好", "description": "经典情感哭哭本",
                "script_type": ScriptType.EMOTION, "difficulty": DifficultyLevel.EASY,
                "min_players": 6, "max_players": 6, "estimated_duration": 240,
                "price": 88.0, "author": "D.", "publisher": "剧鱼文创",
                "publish_year": 2020, "average_rating": 4.5, "total_reviews": 256,
                "is_approved": True,
                "characters": [
                    {"name": "李海泽", "gender": Gender.MALE, "age": 28, "description": "人民警察"},
                    {"name": "于婉儿", "gender": Gender.FEMALE, "age": 31, "description": "公司白领", "is_lead": True},
                    {"name": "梁梓奕", "gender": Gender.MALE, "age": 33, "description": "摄影师"},
                    {"name": "林墨", "gender": Gender.FEMALE, "age": 31, "description": "纹身店老板", "is_lead": True},
                    {"name": "冯坤", "gender": Gender.MALE, "age": 41, "description": "修车厂老板"},
                    {"name": "阿瑶", "gender": Gender.FEMALE, "age": 26, "description": "KTV服务员", "is_lead": True}
                ]
            }
        ]
        
        for script_data in scripts_data:
            chars = script_data.pop("characters")
            script = Script(**script_data, store_id=store_profile.id if store_profile else None)
            db.add(script)
            db.flush()
            for c in chars:
                char = Character(script_id=script.id, **c)
                db.add(char)
        print(f"  ✓ 创建了 {len(scripts_data)} 个剧本")
    else:
        print("  ✓ 已存在剧本，跳过创建")
    print()

    print("[4/7] 创建 DM 排班...")
    dm_profile = db.query(DMProfile).first()
    if dm_profile and db.query(DMSchedule).count() == 0:
        today = date.today()
        for i in range(7):
            s = DMSchedule(
                dm_id=dm_profile.id,
                date=today + timedelta(days=i),
                start_time=time(14, 0),
                end_time=time(22, 0),
                is_available=True
            )
            db.add(s)
        print("  ✓ 创建了 7 天排班")
    else:
        print("  ✓ 排班已存在，跳过")
    print()

    print("[5/7] 创建游戏组局...")
    if db.query(Game).count() == 0:
        store_profile = db.query(StoreProfile).first()
        dm_profile = db.query(DMProfile).first()
        scripts = db.query(Script).all()
        player1 = db.query(User).filter(User.username == "player1").first()
        today = date.today()
        
        games_data = [
            {
                "title": f"{scripts[0].title} - 周末硬核局",
                "script_id": scripts[0].id,
                "game_date": today + timedelta(days=3),
                "start_time": time(19, 0), "end_time": time(23, 0),
                "duration": 240, "max_players": scripts[0].max_players,
                "current_players": 3, "status": GameStatus.RECRUITING,
                "price_per_person": 128.0, "location": store_profile.store_address
            },
            {
                "title": f"{scripts[1].title} - 情感沉浸局",
                "script_id": scripts[1].id,
                "game_date": today + timedelta(days=2),
                "start_time": time(14, 0), "end_time": time(18, 0),
                "duration": 240, "max_players": scripts[1].max_players,
                "current_players": 6, "status": GameStatus.FULL,
                "price_per_person": 88.0, "location": store_profile.store_address
            },
            {
                "title": f"{scripts[0].title} - 已完成局",
                "script_id": scripts[0].id,
                "game_date": today - timedelta(days=1),
                "start_time": time(19, 0), "end_time": time(23, 0),
                "duration": 240, "max_players": scripts[0].max_players,
                "current_players": 5, "status": GameStatus.COMPLETED,
                "price_per_person": 128.0, "location": store_profile.store_address
            }
        ]
        
        for g_data in games_data:
            game = Game(
                **g_data,
                creator_id=player1.id,
                store_id=store_profile.id,
                dm_id=dm_profile.id,
                assignment_method=AssignmentMethod.MANUAL,
                total_price=g_data["price_per_person"] * g_data["max_players"]
            )
            db.add(game)
        db.flush()
        print(f"  ✓ 创建了 {len(games_data)} 个组局")
    else:
        print("  ✓ 组局已存在，跳过")
    print()

    print("[6/7] 创建游戏参与者...")
    if db.query(GameParticipant).count() == 0:
        recruiting_game = db.query(Game).filter(Game.status == GameStatus.RECRUITING).first()
        completed_game = db.query(Game).filter(Game.status == GameStatus.COMPLETED).first()
        player1 = db.query(User).filter(User.username == "player1").first()
        player2 = db.query(User).filter(User.username == "player2").first()
        dm_user = db.query(User).filter(User.username == "dm_user").first()
        admin = db.query(User).filter(User.username == "admin").first()
        
        participants = []
        if recruiting_game:
            participants.extend([
                {"game_id": recruiting_game.id, "user_id": player1.id, "has_paid": True, "payment_amount": recruiting_game.price_per_person},
                {"game_id": recruiting_game.id, "user_id": player2.id, "has_paid": True, "payment_amount": recruiting_game.price_per_person}
            ])
        if completed_game:
            participants.extend([
                {"game_id": completed_game.id, "user_id": player1.id, "has_paid": True, "payment_amount": completed_game.price_per_person},
                {"game_id": completed_game.id, "user_id": player2.id, "has_paid": True, "payment_amount": completed_game.price_per_person},
                {"game_id": completed_game.id, "user_id": admin.id, "has_paid": True, "payment_amount": completed_game.price_per_person}
            ])
        
        for p in participants:
            db.add(GameParticipant(**p))
        print(f"  ✓ 创建了 {len(participants)} 条参与者记录")
    else:
        print("  ✓ 参与者已存在，跳过")
    print()

    print("[7/7] 创建评价和社区帖子...")
    if db.query(Review).count() == 0:
        completed_game = db.query(Game).filter(Game.status == GameStatus.COMPLETED).first()
        if completed_game:
            reviews = [
                Review(game_id=completed_game.id, script_id=completed_game.script_id,
                       author_id=player2.id, rating=5.0, content="非常棒的体验！", is_anonymous=False),
                Review(game_id=completed_game.id, script_id=completed_game.script_id,
                       author_id=admin.id, rating=4.5, content="经典老本名不虚传", is_anonymous=False)
            ]
            for r in reviews:
                db.add(r)
            print(f"  ✓ 创建了 {len(reviews)} 条评价")
    
    if db.query(CommunityPost).count() == 0:
        top_script = db.query(Script).first()
        posts = [
            CommunityPost(title="《年轮》yyds！", content="年度最佳推理本推荐",
                          post_type=PostType.RECOMMENDATION, author_id=player1.id,
                          script_id=top_script.id, tags=["推理", "硬核"],
                          is_hot=True, view_count=1568, like_count=256),
            CommunityPost(title="刚玩完《你好》哭惨了", content="情感本天花板",
                          post_type=PostType.REVIEW, author_id=player2.id,
                          tags=["情感", "哭哭本"], is_hot=True, view_count=2341, like_count=389)
        ]
        for p in posts:
            db.add(p)
        db.flush()
        
        comments = [
            Comment(post_id=posts[0].id, author_id=player2.id, content="同意！", like_count=45),
            Comment(post_id=posts[0].id, author_id=dm_user.id, content="硬核玩家必玩", like_count=89)
        ]
        for c in comments:
            db.add(c)
        print(f"  ✓ 创建了 {len(posts)} 个帖子和 {len(comments)} 条评论")
    
    db.commit()
    print()
    print("=" * 50)
    print("数据库初始化完成！")
    print("=" * 50)
    print("\n测试账号：")
    print("  管理员: admin / admin123")
    print("  DM: dm_user / dm123456")
    print("  店家: store_user / store123")
    print("  玩家1: player1 / player123")
    print("  玩家2: player2 / player123")
    print(f"\n用户数: {db.query(User).count()}")
    print(f"剧本数: {db.query(Script).count()}")
    print(f"游戏数: {db.query(Game).count()}")

except Exception as e:
    db.rollback()
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()
