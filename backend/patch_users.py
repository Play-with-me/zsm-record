with open('app/routers/users.py', 'a', encoding='utf-8') as f:
    f.write('''
@router.get("/me/notifications")
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    from sqlalchemy.future import select
    result = await db.execute(
        select(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .order_by(models.Notification.created_at.desc())
        .limit(20)
    )
    notifs = result.scalars().all()
    return notifs

@router.put("/me/notifications/read")
async def mark_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    from sqlalchemy import update
    await db.execute(
        update(models.Notification)
        .where(models.Notification.user_id == current_user.id)
        .values(is_read=True)
    )
    await db.commit()
    return {"status": "ok"}
''')
print('Appended endpoints.')
