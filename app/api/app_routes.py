from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select
from datetime import timezone
from zoneinfo import ZoneInfo
from app.models.app_models import Users, Remainder
from app.utils.app_validations import CreateRemainder, ListRemainder, DeleteRemainder, CreateUser
from app.database.connection_config import mysession
from app.redis.redis_config import limiter

router = APIRouter()
NEPAL_TZ = ZoneInfo("Asia/Kathmandu")


@router.post('/user/create', status_code=201)
@limiter.limit("5/minute")
async def create_user(request: Request, data: CreateUser):
    async with mysession() as session:
        existing_user = await session.execute(
            select(Users).where(Users.telegram_id == data.telegram_id)
        )
        existing_user = existing_user.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail='User already exists')

        new_user = Users(telegram_id=data.telegram_id)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return {
            "id": new_user.id,
            "telegram_id": new_user.telegram_id,
            "created_at": new_user.created_at
        }


@router.post('/reminder/create', status_code=201)
@limiter.limit("5/minute")
async def create_reminder(request: Request, data: CreateRemainder):
    async with mysession() as session:
        user_check = await session.execute(
            select(Users).where(Users.telegram_id == data.telegram_id)
        )
        user_check = user_check.scalar_one_or_none()
        if not user_check:
            raise HTTPException(status_code=404, detail='User not found')

        duplicate = await session.execute(
            select(Remainder).where(
                Remainder.user_id == user_check.id,
                Remainder.message == data.message,
                Remainder.scheduled_time == data.scheduled_time
            )
        )
        duplicate = duplicate.scalar_one_or_none()
        if duplicate:
            raise HTTPException(status_code=409, detail='Reminder already exists at this time with the same message')

        new_reminder = Remainder(
            user_id=user_check.id,
            message=data.message,
            scheduled_time=data.scheduled_time
        )
        session.add(new_reminder)
        await session.commit()
        await session.refresh(new_reminder)
        return {
            "id": new_reminder.id,
            "message": new_reminder.message,
            "scheduled_time": new_reminder.scheduled_time,
            "is_sent": new_reminder.is_sent
        }


@router.post('/reminder/list', status_code=200)
@limiter.limit("5/minute")
async def list_reminders(request: Request, data: ListRemainder):
    async with mysession() as session:
        user = await session.execute(
            select(Users).where(Users.telegram_id == data.telegram_id)
        )
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        reminders = await session.execute(
            select(Remainder).where(Remainder.user_id == user.id)
        )
        reminders = reminders.scalars().all()
        return [
            {
                "id": r.id,
                "message": r.message,
                "scheduled_time": r.scheduled_time.replace(tzinfo=timezone.utc)
                                   .astimezone(NEPAL_TZ)
                                   .strftime("%Y-%m-%dT%H:%M:%S"),
                "is_sent": r.is_sent,
                "sent_at": r.sent_at.replace(tzinfo=timezone.utc)
                            .astimezone(NEPAL_TZ)
                            .strftime("%Y-%m-%dT%H:%M:%S") if r.sent_at else None
            } for r in reminders
        ]


@router.post('/reminder/delete', status_code=200)
@limiter.limit("5/minute")
async def delete_reminder(request: Request, data: DeleteRemainder):
    async with mysession() as session:
        user = await session.execute(
            select(Users).where(Users.telegram_id == data.telegram_id)
        )
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        reminder = await session.execute(
            select(Remainder).where(
                Remainder.id == data.remainder_id,
                Remainder.user_id == user.id
            )
        )
        reminder = reminder.scalar_one_or_none()
        if not reminder:
            raise HTTPException(status_code=404, detail='Reminder not found')

        await session.delete(reminder)
        await session.commit()
        return {"detail": "Reminder deleted successfully"}
