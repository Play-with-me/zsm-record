from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/record-board", tags=["record-board"])

@router.get("", response_model=List[schemas.RecordBoardEntry])
async def read_record_board(
    map_id: Optional[str] = None, 
    car_id: Optional[str] = None,
    pet_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # This will return the top records dynamically based on filters
    return await crud.get_record_board(db, map_id=map_id, car_id=car_id, pet_id=pet_id)

@router.get("/by-map", response_model=List[schemas.MapLeaderboardEntry])
async def read_record_board_by_map(
    map_id: Optional[str] = None, 
    car_id: Optional[str] = None,
    pet_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Return leaderboard grouped by map, ranked by lowest record time"""
    return await crud.get_record_board_by_map(db, map_id=map_id, car_id=car_id, pet_id=pet_id)

@router.get("/analytics/meta")
async def get_meta_analytics(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    from sqlalchemy import func
    from .. import models
    # Group by car, count videos
    result = await db.execute(
        select(models.Car.name, func.count(models.Video.id).label('count'))
        .join(models.Video, models.Video.car_id == models.Car.id)
        .filter(models.Video.visibility == "PUBLIC")
        .group_by(models.Car.name)
        .order_by(func.count(models.Video.id).desc())
        .limit(10)
    )
    rows = result.all()
    return [{"car": r.name, "count": r.count} for r in rows]

@router.get("/tournaments/active")
async def get_active_tournaments(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    from .. import models
    result = await db.execute(
        select(models.Tournament)
        .filter(models.Tournament.is_active == True)
        .filter(models.Tournament.status == models.TournamentStatusEnum.ONGOING)
    )
    t = result.scalars().first()
    if t:
        return {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "map_id": t.map_id,
            "start_time": t.start_time,
            "end_time": t.end_time
        }
    return None

@router.get("/analytics/meta-pets")
async def get_meta_pets(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    from sqlalchemy import func
    from .. import models
    # Group by pet, count videos
    result = await db.execute(
        select(models.Pet.name, func.count(models.Video.id).label('count'))
        .join(models.Video, models.Video.pet_id == models.Pet.id)
        .filter(models.Video.visibility == "PUBLIC")
        .group_by(models.Pet.name)
        .order_by(func.count(models.Video.id).desc())
        .limit(10)
    )
    rows = result.all()
    return [{"pet": r.name, "count": r.count} for r in rows]

from fastapi import HTTPException
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from .auth import get_current_user
from .. import models, schemas
import math
from typing import List, Optional

@router.post('/tournaments', response_model=schemas.TournamentResponse)
async def create_tournament(
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
    try:
        await db.flush()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi CSDL (1): {str(e)}")
    
    if len(t.participants) > 1 and t.format == 'SINGLE':
        uids = list(t.participants)
        random.shuffle(uids)
        
        parts = []
        for i, uid in enumerate(uids):
            part = models.TournamentParticipant(tournament_id=new_t.id, user_id=uid, seed=i+1)
            db.add(part)
            parts.append(uid)
            
        await db.flush()
        
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
            
        num_r1_matches_needed = num_p - (bracket_size // 2)
        if num_r1_matches_needed < 0: num_r1_matches_needed = 0
        
        r1_assignments = []
        player_idx = 0
        for i in range(bracket_size // 2):
            p1 = None
            p2 = None
            if i < num_r1_matches_needed:
                if player_idx < num_p: p1 = parts[player_idx]
                player_idx += 1
                if player_idx < num_p: p2 = parts[player_idx]
                player_idx += 1
            else:
                if player_idx < num_p: p1 = parts[player_idx]
                player_idx += 1
            r1_assignments.append((p1, p2))
            
        auto_advanced = {}
        # Pre-calculate auto-advanced BYE players for Round 2
        for i in range(bracket_size // 2):
            p1, p2 = r1_assignments[i]
            if p1 and not p2:
                # If this match has only p1 (BYE), p1 auto-advances
                auto_advanced[(2, i // 2, i % 2)] = p1
            
        for r in range(total_rounds, 0, -1):
            matches_in_round = bracket_size // (2 ** r)
            for i in range(matches_in_round):
                mid = matches_dict[(r, i)]
                next_mid = None
                if r < total_rounds:
                    next_mid = matches_dict[(r + 1, i // 2)]
                
                p1_id = None
                p2_id = None
                winner_id = None
                is_completed = False
                
                if r == 1:
                    p1_id, p2_id = r1_assignments[i]
                    if p1_id and not p2_id:
                        winner_id = p1_id
                        is_completed = True
                else:
                    p1_id = auto_advanced.get((r, i, 0))
                    p2_id = auto_advanced.get((r, i, 1))
                    
                m = models.TournamentMatch(
                    id=mid,
                    tournament_id=new_t.id,
                    round_name=get_round_name(r, total_rounds),
                    round_sequence=r,
                    match_index=i,
                    player1_id=p1_id,
                    player2_id=p2_id,
                    winner_id=winner_id,
                    is_completed=is_completed,
                    next_match_id=next_mid
                )
                db.add(m)
            await db.flush()
                
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Lỗi dữ liệu: {str(e)}")

    res = await db.execute(select(models.Tournament).options(selectinload(models.Tournament.map)).filter(models.Tournament.id == new_t.id))
    return res.scalars().first()

@router.get('/tournaments', response_model=List[schemas.TournamentResponse])
async def get_all_tournaments(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(models.Tournament)
            .options(selectinload(models.Tournament.map))
        )
        return result.scalars().all()
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=traceback.format_exc())

@router.get('/tournaments/{t_id}', response_model=schemas.TournamentDetailResponse)
async def get_tournament_detail(t_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Tournament)
        .options(
            selectinload(models.Tournament.map),
            selectinload(models.Tournament.participants).selectinload(models.TournamentParticipant.user),
            selectinload(models.Tournament.matches).selectinload(models.TournamentMatch.player1),
            selectinload(models.Tournament.matches).selectinload(models.TournamentMatch.player2),
            selectinload(models.Tournament.matches).selectinload(models.TournamentMatch.winner)
        )
        .filter(models.Tournament.id == t_id)
    )
    t_obj = result.scalars().first()
    if not t_obj:
        raise HTTPException(status_code=404, detail='Tournament not found')
    return t_obj

@router.put('/tournaments/{t_id}', response_model=schemas.TournamentResponse)
async def update_tournament(
    t_id: str,
    t: schemas.TournamentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail='Forbidden')
    
    result = await db.execute(select(models.Tournament).filter(models.Tournament.id == t_id))
    t_obj = result.scalars().first()
    if not t_obj: raise HTTPException(status_code=404, detail='Tournament not found')
    
    update_data = t.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(t_obj, key, value)
    
    await db.commit()
    
    res = await db.execute(select(models.Tournament).options(selectinload(models.Tournament.map)).filter(models.Tournament.id == t_id))
    return res.scalars().first()

@router.delete('/tournaments/{t_id}')
async def delete_tournament(
    t_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail='Forbidden')
    
    result = await db.execute(select(models.Tournament).filter(models.Tournament.id == t_id))
    t_obj = result.scalars().first()
    if not t_obj: raise HTTPException(status_code=404, detail='Tournament not found')
    
    await db.delete(t_obj)
    await db.commit()
    return {'message': 'Deleted tournament'}

class ParticipantAdd(BaseModel):
    user_id: str
    seed: Optional[int] = None

@router.post('/tournaments/{t_id}/participants', response_model=schemas.TournamentParticipantResponse)
async def add_participant(
    t_id: str,
    p: ParticipantAdd,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail='Forbidden')
        
    part = models.TournamentParticipant(tournament_id=t_id, user_id=p.user_id, seed=p.seed)
    db.add(part)
    await db.commit()
    await db.refresh(part)
    
    res = await db.execute(select(models.TournamentParticipant).options(selectinload(models.TournamentParticipant.user)).filter(models.TournamentParticipant.id == part.id))
    return res.scalars().first()

@router.delete('/tournaments/{t_id}/participants/{user_id}')
async def remove_participant(
    t_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail='Forbidden')
        
    res = await db.execute(select(models.TournamentParticipant).filter(models.TournamentParticipant.tournament_id == t_id, models.TournamentParticipant.user_id == user_id))
    part = res.scalars().first()
    if part:
        await db.delete(part)
        await db.commit()
    return {'message': 'Removed'}

@router.post('/tournaments/{t_id}/generate')
async def generate_bracket(
    t_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail='Forbidden')
        
    res = await db.execute(select(models.Tournament).options(selectinload(models.Tournament.participants)).filter(models.Tournament.id == t_id))
    t_obj = res.scalars().first()
    if not t_obj: raise HTTPException(status_code=404, detail='Tournament not found')
    
    if t_obj.format != models.TournamentFormatEnum.SINGLE:
        raise HTTPException(status_code=400, detail='Only SINGLE format is supported for auto-generation right now')
        
    # Delete existing matches
    await db.execute(models.TournamentMatch.__table__.delete().where(models.TournamentMatch.tournament_id == t_id))
    
    participants = list(t_obj.participants)
    num_p = len(participants)
    if num_p < 2: raise HTTPException(status_code=400, detail='Need at least 2 participants')
    
    # Calculate next power of 2
    bracket_size = 2 ** math.ceil(math.log2(num_p))
    total_rounds = int(math.log2(bracket_size))
    
    matches_dict = {} 
    from ..models import generate_uuid
    
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
            
            # Fill players for Round 1
            if r == 1:
                idx1 = i * 2
                idx2 = i * 2 + 1
                if idx1 < num_p: p1_id = participants[idx1].user_id
                if idx2 < num_p: p2_id = participants[idx2].user_id
                
            m = models.TournamentMatch(
                id=mid,
                tournament_id=t_id,
                round_name=get_round_name(r, total_rounds),
                round_sequence=r,
                match_index=i,
                player1_id=p1_id,
                player2_id=p2_id,
                next_match_id=next_mid
            )
            db.add(m)
            
    t_obj.status = models.TournamentStatusEnum.ONGOING
    await db.commit()
    return {'message': 'Generated'}

class MatchUpdate(BaseModel):
    player1_id: Optional[str] = None
    player2_id: Optional[str] = None
    winner_id: Optional[str] = None

@router.put('/tournaments/{t_id}/matches/{m_id}', response_model=schemas.TournamentMatchResponse)
async def update_match(
    t_id: str,
    m_id: str,
    m_upd: MatchUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail='Forbidden')
        
    res = await db.execute(select(models.TournamentMatch).filter(models.TournamentMatch.id == m_id, models.TournamentMatch.tournament_id == t_id))
    m = res.scalars().first()
    if not m: raise HTTPException(status_code=404, detail='Match not found')
    
    if m_upd.player1_id is not None: m.player1_id = m_upd.player1_id if m_upd.player1_id else None
    if m_upd.player2_id is not None: m.player2_id = m_upd.player2_id if m_upd.player2_id else None
    
    if m_upd.winner_id is not None:
        if m_upd.winner_id == '':
            m.winner_id = None
            m.is_completed = False
        else:
            m.winner_id = m_upd.winner_id
            m.is_completed = True
            
            # Advance winner to next match
            if m.next_match_id:
                next_res = await db.execute(select(models.TournamentMatch).filter(models.TournamentMatch.id == m.next_match_id))
                nm = next_res.scalars().first()
                if nm:
                    if m.match_index % 2 == 0:
                        nm.player1_id = m.winner_id
                    else:
                        nm.player2_id = m.winner_id
                    
    await db.commit()
    
    res = await db.execute(
        select(models.TournamentMatch)
        .options(
            selectinload(models.TournamentMatch.player1),
            selectinload(models.TournamentMatch.player2),
            selectinload(models.TournamentMatch.winner)
        )
        .filter(models.TournamentMatch.id == m_id)
    )
    return res.scalars().first()
