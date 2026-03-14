from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo
from sqlalchemy import select, update
from app.database.connection_config import mysession
from app.models.app_models import Users, Remainder

NEPAL_TZ = ZoneInfo('Asia/Kathmandu')


async def send_reminders(bot):
    try:
        async with mysession() as session:
            now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

            result = await session.execute(
                select(Remainder).where(
                    Remainder.is_sent == False,
                    Remainder.scheduled_time <= now_utc
                )
            )
            reminders = result.scalars().all()

            if not reminders:
                return

            for reminder in reminders:
                try:
                    user_result = await session.execute(
                        select(Users).where(Users.id == reminder.user_id)
                    )
                    user = user_result.scalar_one_or_none()

                    if not user:
                        print(f"⚠️ User not found for reminder {reminder.id}, skipping.")
                        continue

                    # Convert UTC → Nepal time for display
                    scheduled_nepal = reminder.scheduled_time.replace(
                        tzinfo=timezone.utc
                    ).astimezone(NEPAL_TZ).strftime("%Y-%m-%dT%H:%M:%S")

                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=(
                            f"🔔 *Reminder!*\n\n"
                            f"📝 {reminder.message}\n\n"
                            f"🕐 `{scheduled_nepal}` 🇳🇵"
                        ),
                        parse_mode="Markdown"
                    )

                    await session.execute(
                        update(Remainder)
                        .where(Remainder.id == reminder.id)
                        .values(
                            is_sent=True,
                            sent_at=datetime.now(timezone.utc).replace(tzinfo=None)
                        )
                    )
                    await session.commit()
                    print(f"✅ Reminder {reminder.id} sent to {user.telegram_id}")

                except Exception as e:
                    print(f"❌ Failed to send reminder {reminder.id}: {e}")
                    continue

    except Exception as e:
        print(f"❌ Scheduler error: {e}")


def start_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone=timezone.utc)

    scheduler.add_job(
        send_reminders,
        trigger="interval",
        seconds=30,
        args=[bot],
        id="remainder_checker",
        replace_existing=True
        
    )
    scheduler.start()
    print("🕐 Scheduler started — checking every 30 seconds")
    return scheduler