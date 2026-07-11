import re

with open('backend/app/routers/videos.py', 'r', encoding='utf-8') as f:
    c = f.read()

new_routes = '''
@router.post("/{video_id}/unlike")
async def unlike_video(
    video_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_current_user),
):
    db_video = await crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
        
    if db_video.likes > 0:
        db_video.likes -= 1
        await db.commit()
    return {"message": "Unliked successfully", "likes": db_video.likes}

@router.delete("/{video_id}/comments/{comment_id}")
async def delete_comment(
    video_id: str,
    comment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_video = await crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
        
    comment = await crud.get_comment(db, comment_id=comment_id)
    if comment is None or comment.video_id != video_id:
        raise HTTPException(status_code=404, detail="Comment not found")
        
    if comment.user_id != current_user.id and current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
        
    await crud.delete_comment(db, comment)
    return {"message": "Comment deleted"}
'''

if 'unlike_video' not in c:
    c = c + '\n' + new_routes
    with open('backend/app/routers/videos.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print('videos.py updated')
else:
    print('Routes already exist in videos.py')
