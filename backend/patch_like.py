with open('app/routers/videos.py', 'r', encoding='utf-8') as f:
    js = f.read()

old_like = '''    db_video.likes += 1
    await db.commit()
    return {"message": "Liked successfully", "likes": db_video.likes}'''

new_like = '''    db_video.likes += 1
    
    # Add EXP and Notification to video owner
    if current_user and current_user.id != db_video.user_id:
        owner = await db.get(models.User, db_video.user_id)
        if owner:
            owner.exp += 10
            notif = models.Notification(
                user_id=owner.id,
                message=f"{current_user.username} đã thích kỷ lục của bạn!"
            )
            db.add(notif)
            
    await db.commit()
    return {"message": "Liked successfully", "likes": db_video.likes}'''

js = js.replace(old_like, new_like)

with open('app/routers/videos.py', 'w', encoding='utf-8') as f:
    f.write(js)
