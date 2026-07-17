import re

with open(r'backend\app\routers\board.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new full create_tournament function
new_func = '''async def create_tournament(
    t: schemas.TournamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail='Forbidden')
    
    import random
    import math
    from ..models import generate_uuid
    
    new_t = models.Tournament(
        name=t.name,
        description=t.description,
        map_id=t.map_id,
        start_time=t.start_time,
        end_time=t.end_time,
        is_active=t.is_active,
        format=t.format,
        status=models.TournamentStatusEnum.ONGOING if len(t.participants) > 1 else models.TournamentStatusEnum.DRAFT
    )
    db.add(new_t)
    await db.commit()
    await db.refresh(new_t)
    
    if len(t.participants) > 1 and t.format.value == 'SINGLE':
        uids = list(t.participants)
        random.shuffle(uids)
        
        parts = []
        for i, uid in enumerate(uids):
            part = models.TournamentParticipant(tournament_id=new_t.id, user_id=uid, seed=i+1)
            db.add(part)
            parts.append(uid)
            
        await db.commit()
        
        num_p = len(parts)
        bracket_size = 2 ** math.ceil(math.log2(num_p))
        total_rounds = int(math.log2(bracket_size))
        
        matches_dict = {} 
        for r in range(1, total_rounds + 1):
            matches_in_round = bracket_size // (2 ** r)
            for i in range(matches_in_round):
                matches_dict[(r, i)] = generate_uuid()
                
        def get_round_name(r, total):
            if r == total: return "Chung Kết"
            if r == total - 1: return "Bán Kết"
            if r == total - 2: return "Tứ Kết"
            return f"Vòng {r}"
            
        for r in range(1, total_rounds + 1):
            matches_in_round = bracket_size // (2 ** r)
            for i in range(matches_in_round):
                mid = matches_dict[(r, i)]
                next_mid = None
                if r < total_rounds:
                    next_mid = matches_dict[(r + 1, i // 2)]
                
                p1_id = None
                p2_id = None
                
                if r == 1:
                    idx1 = i * 2
                    idx2 = i * 2 + 1
                    if idx1 < num_p: p1_id = parts[idx1]
                    if idx2 < num_p: p2_id = parts[idx2]
                    
                m = models.TournamentMatch(
                    id=mid,
                    tournament_id=new_t.id,
                    round_name=get_round_name(r, total_rounds),
                    round_sequence=r,
                    match_index=i,
                    player1_id=p1_id,
                    player2_id=p2_id,
                    next_match_id=next_mid
                )
                db.add(m)
                
        await db.commit()

    res = await db.execute(select(models.Tournament).options(selectinload(models.Tournament.map)).filter(models.Tournament.id == new_t.id))
    return res.scalars().first()'''

# Use regex to replace everything from async def create_tournament to return res.scalars().first()
pattern = re.compile(r'async def create_tournament\(.*?return res\.scalars\(\)\.first\(\)', re.DOTALL)
content = pattern.sub(new_func, content)

with open(r'backend\app\routers\board.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed board.py")
