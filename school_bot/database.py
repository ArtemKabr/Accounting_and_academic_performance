import aiosqlite

# Инициализация базы
async def init_db():
    async with aiosqlite.connect("schedule.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weekday TEXT,
                subject TEXT,
                subject_order INTEGER
            )
        """)
        await db.commit()

# Сохранение расписания
async def save_schedule(weekday, subjects):
    async with aiosqlite.connect("schedule.db") as db:
        await db.execute("DELETE FROM schedule WHERE weekday = ?", (weekday,))
        for i, subject in enumerate(subjects):
            await db.execute(
                "INSERT INTO schedule (weekday, subject, subject_order) VALUES (?, ?, ?)",
                (weekday, subject, i)
            )
        await db.commit()

# Получение расписания по дню
async def get_schedule_for_day(weekday):
    async with aiosqlite.connect("schedule.db") as db:
        cursor = await db.execute(
            "SELECT subject FROM schedule WHERE weekday = ? ORDER BY subject_order", (weekday,)
        )
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
