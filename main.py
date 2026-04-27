# from fastapi import FastAPI 

# app = FastAPI()

# @app.get("/")
# def root():
#     return {"message": "Hello TP Cloud", "status": "working"}

# @app.get("/health")
# def health():
#     return {"status": "healthy", "server": "running"}

# @app.get("/test")
# def test():
#     return {"message": "test is successful"}




# SQLITE


# from fastapi import FastAPI, HTTPException, Query
# from pydantic import BaseModel
# from typing import List, Optional, Dict, Any
# import sqlite3
# import pymongo
# from datetime import datetime
# import os

# # ==============================================
# # 1. إنشاء تطبيق FastAPI
# # ==============================================
# app = FastAPI(
#     title="TP Cloud API - Phase 2",
#     description="API avec SQLite (relationnelle) + MongoDB (NoSQL)",
#     version="2.0.0"
# )

# # ==============================================
# # 2. قاعدة البيانات العلائقية: SQLite
# # ==============================================

# # إنشاء مجلد للبيانات إذا لم يكن موجودًا
# os.makedirs("data", exist_ok=True)

# # الاتصال بقاعدة SQLite
# sql_conn = sqlite3.connect("data/tp_cloud.db", check_same_thread=False)
# sql_cursor = sql_conn.cursor()

# # إنشاء الجداول
# sql_cursor.execute("""
# CREATE TABLE IF NOT EXISTS students (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL,
#     email TEXT UNIQUE NOT NULL,
#     filiere TEXT NOT NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# )
# """)

# sql_cursor.execute("""
# CREATE TABLE IF NOT EXISTS courses (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     title TEXT NOT NULL,
#     credits INTEGER DEFAULT 3,
#     teacher TEXT NOT NULL
# )
# """)

# sql_cursor.execute("""
# CREATE TABLE IF NOT EXISTS inscriptions (
#     student_id INTEGER,
#     course_id INTEGER,
#     date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (student_id) REFERENCES students(id),
#     FOREIGN KEY (course_id) REFERENCES courses(id),
#     PRIMARY KEY (student_id, course_id)
# )
# """)

# sql_conn.commit()

# # ==============================================
# # 3. قاعدة البيانات غير العلائقية: MongoDB
# # ==============================================

# # محاولة الاتصال بـ MongoDB (محلي أو سحابي)
# MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
# mongo_client = None
# mongo_db = None
# logs_collection = None
# activities_collection = None

# try:
#     mongo_client = pymongo.MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
#     # اختبار الاتصال
#     mongo_client.admin.command('ping')
#     mongo_db = mongo_client["tp_cloud_nosql"]
#     logs_collection = mongo_db["logs"]
#     activities_collection = mongo_db["activities"]
#     print("✅ MongoDB connecté avec succès")
# except Exception as e:
#     print(f"⚠️ MongoDB non disponible: {e}")
#     print("⚠️ Le mode NoSQL sera limité (données en mémoire)")
#     # وضع محاكاة (mock) في حالة عدم توفر MongoDB
#     mock_logs = []
#     mock_activities = []

# # ==============================================
# # 4. نماذج البيانات (Pydantic)
# # ==============================================

# class Student(BaseModel):
#     name: str
#     email: str
#     filiere: str

# class StudentResponse(Student):
#     id: int
#     created_at: str

# class Course(BaseModel):
#     title: str
#     credits: int = 3
#     teacher: str

# class CourseResponse(Course):
#     id: int

# class Inscription(BaseModel):
#     student_id: int
#     course_id: int

# class Log(BaseModel):
#     action: str
#     entity: str
#     entity_id: int
#     details: str = ""

# class ActivityLog(BaseModel):
#     user_action: str
#     timestamp: str
#     data: Dict[str, Any]

# # ==============================================
# # 5. دوال مساعدة لتسجيل النشاطات في NoSQL
# # ==============================================

# def log_to_nosql(action: str, entity: str, entity_id: int, details: str = ""):
#     """تسجيل أي حدث في قاعدة NoSQL"""
#     log_entry = {
#         "action": action,
#         "entity": entity,
#         "entity_id": entity_id,
#         "details": details,
#         "timestamp": datetime.now().isoformat()
#     }
    
#     if logs_collection is not None:
#         logs_collection.insert_one(log_entry)
#         print(f"📝 Logged to MongoDB: {action}")
#     else:
#         # وضع المحاكاة
#         mock_logs.append(log_entry)
    
#     return log_entry

# def get_all_logs_from_nosql():
#     """جلب جميع السجلات من NoSQL"""
#     if logs_collection is not None:
#         return list(logs_collection.find({}, {"_id": 0}))
#     else:
#         return mock_logs

# # ==============================================
# # 6. API Endpoints للطلاب (SQL)
# # ==============================================

# @app.get("/sql/students", response_model=List[StudentResponse])
# def get_all_students():
#     """جلب جميع الطلاب من قاعدة SQL"""
#     sql_cursor.execute("SELECT id, name, email, filiere, created_at FROM students")
#     students = sql_cursor.fetchall()
    
#     # تسجيل النشاط في NoSQL
#     log_to_nosql("READ_ALL", "students", 0, f"Retrieved {len(students)} students")
    
#     return [
#         {
#             "id": s[0], 
#             "name": s[1], 
#             "email": s[2], 
#             "filiere": s[3],
#             "created_at": s[4]
#         } 
#         for s in students
#     ]

# @app.get("/sql/students/{student_id}", response_model=StudentResponse)
# def get_student_by_id(student_id: int):
#     """جلب طالب محدد من SQL"""
#     sql_cursor.execute(
#         "SELECT id, name, email, filiere, created_at FROM students WHERE id = ?", 
#         (student_id,)
#     )
#     student = sql_cursor.fetchone()
    
#     if not student:
#         raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
#     # تسجيل النشاط في NoSQL
#     log_to_nosql("READ_ONE", "students", student_id, f"Retrieved student: {student[1]}")
    
#     return {
#         "id": student[0],
#         "name": student[1],
#         "email": student[2],
#         "filiere": student[3],
#         "created_at": student[4]
#     }

# @app.post("/sql/students", response_model=StudentResponse)
# def create_student(student: Student):
#     """إضافة طالب جديد في SQL"""
#     try:
#         sql_cursor.execute(
#             "INSERT INTO students (name, email, filiere) VALUES (?, ?, ?)",
#             (student.name, student.email, student.filiere)
#         )
#         sql_conn.commit()
#         student_id = sql_cursor.lastrowid
        
#         # تسجيل النشاط في NoSQL
#         log_to_nosql("CREATE", "students", student_id, f"Created student: {student.name}")
        
#         return {
#             "id": student_id,
#             "name": student.name,
#             "email": student.email,
#             "filiere": student.filiere,
#             "created_at": datetime.now().isoformat()
#         }
#     except sqlite3.IntegrityError:
#         raise HTTPException(status_code=400, detail=f"Email {student.email} already exists")

# @app.put("/sql/students/{student_id}", response_model=StudentResponse)
# def update_student(student_id: int, student: Student):
#     """تحديث بيانات طالب في SQL"""
#     # التأكد من وجود الطالب
#     sql_cursor.execute("SELECT id, name, email, filiere, created_at FROM students WHERE id = ?", (student_id,))
#     existing_student = sql_cursor.fetchone()
    
#     if not existing_student:
#         raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
#     # تنفيذ التحديث
#     sql_cursor.execute(
#         "UPDATE students SET name = ?, email = ?, filiere = ? WHERE id = ?",
#         (student.name, student.email, student.filiere, student_id)
#     )
#     sql_conn.commit()
    
#     # تسجيل النشاط في NoSQL
#     log_to_nosql("UPDATE", "students", student_id, f"Updated student: {student.name}")
    
#     # إرجاع البيانات المحدثة (مع created_at القديم)
#     return {
#         "id": student_id,
#         "name": student.name,
#         "email": student.email,
#         "filiere": student.filiere,
#         "created_at": existing_student[4]  # created_at من السجل القديم
#     }

# @app.delete("/sql/students/{student_id}")
# def delete_student(student_id: int):
#     """حذف طالب من SQL"""
#     # جلب الاسم للتسجيل
#     sql_cursor.execute("SELECT name FROM students WHERE id = ?", (student_id,))
#     student = sql_cursor.fetchone()
    
#     if not student:
#         raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
#     sql_cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
#     sql_conn.commit()
    
#     # تسجيل النشاط في NoSQL
#     log_to_nosql("DELETE", "students", student_id, f"Deleted student: {student[0]}")
    
#     return {"message": f"Student {student_id} deleted successfully"}

# # ==============================================
# # 7. API Endpoints للمواد الدراسية (SQL)
# # ==============================================

# @app.get("/sql/courses", response_model=List[CourseResponse])
# def get_all_courses():
#     """جلب جميع المواد من SQL"""
#     sql_cursor.execute("SELECT id, title, credits, teacher FROM courses")
#     courses = sql_cursor.fetchall()
    
#     log_to_nosql("READ_ALL", "courses", 0, f"Retrieved {len(courses)} courses")
    
#     return [{"id": c[0], "title": c[1], "credits": c[2], "teacher": c[3]} for c in courses]

# @app.post("/sql/courses", response_model=CourseResponse)
# def create_course(course: Course):
#     """إضافة مادة جديدة في SQL"""
#     sql_cursor.execute(
#         "INSERT INTO courses (title, credits, teacher) VALUES (?, ?, ?)",
#         (course.title, course.credits, course.teacher)
#     )
#     sql_conn.commit()
#     course_id = sql_cursor.lastrowid
    
#     log_to_nosql("CREATE", "courses", course_id, f"Created course: {course.title}")
    
#     return {
#         "id": course_id,
#         "title": course.title,
#         "credits": course.credits,
#         "teacher": course.teacher
#     }

# @app.post("/sql/inscriptions")
# def inscribe_student(inscription: Inscription):
#     """تسجيل طالب في مادة (علاقة many-to-many)"""
#     try:
#         sql_cursor.execute(
#             "INSERT INTO inscriptions (student_id, course_id) VALUES (?, ?)",
#             (inscription.student_id, inscription.course_id)
#         )
#         sql_conn.commit()
        
#         log_to_nosql(
#             "CREATE", "inscriptions", 0, 
#             f"Student {inscription.student_id} inscribed in course {inscription.course_id}"
#         )
        
#         return {"message": "Student inscribed successfully"}
#     except sqlite3.IntegrityError:
#         raise HTTPException(status_code=400, detail="Inscription already exists or invalid IDs")

# @app.get("/sql/students/{student_id}/courses")
# def get_student_courses(student_id: int):
#     """جلب المواد التي يدرسها طالب معين"""
#     sql_cursor.execute("""
#         SELECT c.id, c.title, c.credits, c.teacher, i.date_inscription
#         FROM courses c
#         JOIN inscriptions i ON c.id = i.course_id
#         WHERE i.student_id = ?
#     """, (student_id,))
    
#     courses = sql_cursor.fetchall()
    
#     return {
#         "student_id": student_id,
#         "courses": [
#             {
#                 "id": c[0],
#                 "title": c[1],
#                 "credits": c[2],
#                 "teacher": c[3],
#                 "inscription_date": c[4]
#             }
#             for c in courses
#         ]
#     }

# # ==============================================
# # 8. API Endpoints لـ NoSQL (السجلات والنشاطات)
# # ==============================================

# @app.get("/nosql/logs")
# def get_nosql_logs(limit: int = Query(50, le=100)):
#     """جلب آخر السجلات من NoSQL"""
#     logs = get_all_logs_from_nosql()
#     return {
#         "total": len(logs),
#         "logs": logs[-limit:]  # آخر limit سجل
#     }

# @app.get("/nosql/stats")
# def get_nosql_statistics():
#     """إحصائيات عن النشاطات من NoSQL"""
#     logs = get_all_logs_from_nosql()
    
#     # حساب الإحصائيات
#     stats = {
#         "total_actions": len(logs),
#         "actions_by_type": {},
#         "entities_by_type": {}
#     }
    
#     for log in logs:
#         action = log.get("action", "UNKNOWN")
#         entity = log.get("entity", "UNKNOWN")
        
#         stats["actions_by_type"][action] = stats["actions_by_type"].get(action, 0) + 1
#         stats["entities_by_type"][entity] = stats["entities_by_type"].get(entity, 0) + 1
    
#     return stats

# @app.post("/nosql/activity")
# def add_activity_log(activity: ActivityLog):
#     """إضافة سجل نشاط مباشر إلى NoSQL"""
#     if activities_collection is not None:
#         activities_collection.insert_one(activity.dict())
#         return {"message": "Activity logged"}
#     else:
#         mock_activities.append(activity.dict())
#         return {"message": "Activity logged (mock mode)"}

# # ==============================================
# # 9. API يجمع بين SQL و NoSQL
# # ==============================================

# @app.get("/combined/dashboard")
# def get_combined_dashboard():
#     """لوحة تحكم تجمع بيانات SQL و NoSQL معًا"""
    
#     # بيانات من SQL
#     sql_cursor.execute("SELECT COUNT(*) FROM students")
#     total_students = sql_cursor.fetchone()[0]
    
#     sql_cursor.execute("SELECT COUNT(*) FROM courses")
#     total_courses = sql_cursor.fetchone()[0]
    
#     sql_cursor.execute("""
#         SELECT s.name, COUNT(i.course_id) as courses_count
#         FROM students s
#         LEFT JOIN inscriptions i ON s.id = i.student_id
#         GROUP BY s.id
#         ORDER BY courses_count DESC
#         LIMIT 5
#     """)
#     top_students = [{"name": row[0], "courses": row[1]} for row in sql_cursor.fetchall()]
    
#     # بيانات من NoSQL
#     logs = get_all_logs_from_nosql()
#     recent_actions = logs[-10:] if logs else []
    
#     # إحصائيات النشاطات
#     action_counts = {}
#     for log in logs:
#         action = log.get("action", "UNKNOWN")
#         action_counts[action] = action_counts.get(action, 0) + 1
    
#     return {
#         "sql_data": {
#             "total_students": total_students,
#             "total_courses": total_courses,
#             "top_5_active_students": top_students
#         },
#         "nosql_data": {
#             "total_audit_logs": len(logs),
#             "recent_actions": recent_actions,
#             "action_statistics": action_counts
#         },
#         "summary": {
#             "message": "Data combined from SQL (students/courses) and NoSQL (audit logs)",
#             "api_version": "2.0.0"
#         }
#     }

# # ==============================================
# # 10. Endpoints للاختبار والصحة
# # ==============================================

# @app.get("/")
# def root():
#     """الصفحة الرئيسية"""
#     return {
#         "message": "TP Cloud API - Phase 2",
#         "status": "running",
#         "databases": {
#             "sql": "SQLite (connected)",
#             "nosql": "MongoDB (connected)" if logs_collection is not None else "MongoDB (mock mode)"
#         },
#         "endpoints": {
#             "sql_students": "/sql/students (GET, POST)",
#             "sql_students_id": "/sql/students/{id} (GET, PUT, DELETE)",
#             "sql_courses": "/sql/courses (GET, POST)",
#             "sql_inscriptions": "/sql/inscriptions (POST)",
#             "nosql_logs": "/nosql/logs (GET)",
#             "nosql_stats": "/nosql/stats (GET)",
#             "combined": "/combined/dashboard (GET)",
#             "docs": "/docs"
#         }
#     }

# @app.get("/health")
# def health_check():
#     """فحص صحة التطبيق وقواعد البيانات"""
#     health_status = {
#         "status": "healthy",
#         "timestamp": datetime.now().isoformat(),
#         "sqlite": "connected",
#         "mongodb": "connected" if logs_collection is not None else "mock_mode",
#         "sql_tables": []
#     }
    
#     # فحص جداول SQL
#     sql_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
#     health_status["sql_tables"] = [row[0] for row in sql_cursor.fetchall()]
    
#     return health_status

# @app.get("/seed")
# def seed_demo_data():
#     """إضافة بيانات تجريبية للاختبار"""
    
#     # إضافة طلاب تجريبيين
#     demo_students = [
#         ("Ahmed Benali", "ahmed@example.com", "Informatique"),
#         ("Sara Kadi", "sara@example.com", "Réseaux"),
#         ("Mohamed Lamine", "mohamed@example.com", "Informatique"),
#         ("Fatima Zohra", "fatima@example.com", "Mathématiques"),
#         ("Yacine Ouali", "yacine@example.com", "Réseaux"),
#     ]
    
#     for name, email, filiere in demo_students:
#         try:
#             sql_cursor.execute(
#                 "INSERT INTO students (name, email, filiere) VALUES (?, ?, ?)",
#                 (name, email, filiere)
#             )
#         except sqlite3.IntegrityError:
#             pass  # الإيميل موجود مسبقًا
    
#     # إضافة مواد تجريبية
#     demo_courses = [
#         ("Cloud Computing", 5, "Dr. Amir"),
#         ("Big Data", 4, "Dr. Nadia"),
#         ("Machine Learning", 4, "Dr. Karim"),
#         ("DevOps", 3, "Mme Leila"),
#     ]
    
#     for title, credits, teacher in demo_courses:
#         sql_cursor.execute(
#             "INSERT OR IGNORE INTO courses (title, credits, teacher) VALUES (?, ?, ?)",
#             (title, credits, teacher)
#         )
    
#     sql_conn.commit()
    
#     # تسجيل العملية في NoSQL
#     log_to_nosql("SEED", "database", 0, "Added demo data")
    
#     return {"message": "Demo data seeded successfully"}

# # عند تشغيل الملف مباشرة
# if __name__ == "__main__":
#     import uvicorn
#     print(" Starting TP Cloud API - Phase 2...")
#     print("SQLite: data/tp_cloud.db")
#     print(" MongoDB: " + (MONGO_URL if mongo_client else "Not connected (mock mode)"))
#     print("API Docs: http://127.0.0.1:8000/docs")
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


 #MongoDB
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any
import pymongo
from datetime import datetime
import os
from sqlalchemy import create_engine, text

# ==============================================
# 1. إنشاء تطبيق FastAPI
# ==============================================
app = FastAPI(
    title="TP Cloud API - Phase 2",
    description="API avec PostgreSQL (relationnelle) + MongoDB Atlas (NoSQL)",
    version="2.0.0"
)

# ==============================================
# 2. قاعدة البيانات العلائقية: PostgreSQL (على Render)
# ==============================================

# خذ الرابط من Render PostgreSQL Dashboard
# مثال: postgresql://tp_user:password@dpg-xxxxx-a.frankfurt-postgres.render.com:5432/tp_cloud
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tp_user:QiapSP2tTM6zwSOfkpJFA5t3wlNIiSJ9@dpg-d7nq40a8qa3s73adgnsg-a.frankfurt-postgres.render.com/tp_cloud_b5v9")

# إنشاء محرك الاتصال
engine = create_engine(DATABASE_URL)

def init_postgres_db():
    """إنشاء الجداول في PostgreSQL إذا لم تكن موجودة"""
    try:
        with engine.connect() as conn:
            # إنشاء جدول students
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    filiere TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # إنشاء جدول courses
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS courses (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    credits INTEGER DEFAULT 3,
                    teacher TEXT NOT NULL
                )
            """))
            
            # إنشاء جدول inscriptions
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS inscriptions (
                    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                    date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (student_id, course_id)
                )
            """))
            
            conn.commit()
            print("✅ PostgreSQL tables created/verified successfully!")
    except Exception as e:
        print(f"⚠️ Error creating tables: {e}")

# استدعاء الدالة عند بدء التشغيل
init_postgres_db()

# ==============================================
# 3. قاعدة البيانات غير العلائقية: MongoDB Atlas
# ==============================================

# رابط MongoDB Atlas (خذه من موقع MongoDB Atlas)
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://username:password@cluster0.xxx.mongodb.net/")

mongo_client = None
mongo_db = None
logs_collection = None
activities_collection = None
mock_logs = []
mock_activities = []

try:
    mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping')
    mongo_db = mongo_client["tp_cloud_nosql"]
    logs_collection = mongo_db["logs"]
    activities_collection = mongo_db["activities"]
    print("✅ MongoDB Atlas connected successfully!")
except Exception as e:
    print(f"⚠️ MongoDB Atlas not available: {e}")
    print("⚠️ Using mock mode for NoSQL")

# ==============================================
# 4. نماذج البيانات (Pydantic)
# ==============================================

class Student(BaseModel):
    name: str
    email: str
    filiere: str

class StudentResponse(Student):
    id: int
    created_at: str

class Course(BaseModel):
    title: str
    credits: int = 3
    teacher: str

class CourseResponse(Course):
    id: int

class Inscription(BaseModel):
    student_id: int
    course_id: int

class ActivityLog(BaseModel):
    user_action: str
    timestamp: str
    data: Dict[str, Any]

# ==============================================
# 5. دوال مساعدة لتسجيل النشاطات في NoSQL
# ==============================================

def log_to_nosql(action: str, entity: str, entity_id: int, details: str = ""):
    """تسجيل أي حدث في قاعدة NoSQL"""
    log_entry = {
        "action": action,
        "entity": entity,
        "entity_id": entity_id,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    
    if logs_collection is not None:
        logs_collection.insert_one(log_entry)
        print(f"📝 Logged to MongoDB: {action}")
    else:
        mock_logs.append(log_entry)
    
    return log_entry

def get_all_logs_from_nosql():
    """جلب جميع السجلات من NoSQL"""
    if logs_collection is not None:
        return list(logs_collection.find({}, {"_id": 0}))
    else:
        return mock_logs

# ==============================================
# 6. API Endpoints للطلاب (PostgreSQL)
# ==============================================

@app.get("/sql/students", response_model=List[StudentResponse])
def get_all_students():
    """جلب جميع الطلاب من قاعدة PostgreSQL"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name, email, filiere, created_at FROM students ORDER BY id"))
        students = result.fetchall()
    
    log_to_nosql("READ_ALL", "students", 0, f"Retrieved {len(students)} students")
    
    return [
        {
            "id": s[0], 
            "name": s[1], 
            "email": s[2], 
            "filiere": s[3],
            "created_at": str(s[4])
        } 
        for s in students
    ]

@app.get("/sql/students/{student_id}", response_model=StudentResponse)
def get_student_by_id(student_id: int):
    """جلب طالب محدد من PostgreSQL"""
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, name, email, filiere, created_at FROM students WHERE id = :id"),
            {"id": student_id}
        )
        student = result.fetchone()
    
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
    log_to_nosql("READ_ONE", "students", student_id, f"Retrieved student: {student[1]}")
    
    return {
        "id": student[0],
        "name": student[1],
        "email": student[2],
        "filiere": student[3],
        "created_at": str(student[4])
    }

@app.post("/sql/students", response_model=StudentResponse)
def create_student(student: Student):
    """إضافة طالب جديد في PostgreSQL"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO students (name, email, filiere) 
                    VALUES (:name, :email, :filiere) 
                    RETURNING id, created_at
                """),
                {"name": student.name, "email": student.email, "filiere": student.filiere}
            )
            conn.commit()
            new_student = result.fetchone()
            student_id = new_student[0]
            created_at = str(new_student[1])
        
        log_to_nosql("CREATE", "students", student_id, f"Created student: {student.name}")
        
        return {
            "id": student_id,
            "name": student.name,
            "email": student.email,
            "filiere": student.filiere,
            "created_at": created_at
        }
    except Exception as e:
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail=f"Email {student.email} already exists")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/sql/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: Student):
    """تحديث بيانات طالب في PostgreSQL"""
    with engine.connect() as conn:
        # التحقق من وجود الطالب
        check = conn.execute(text("SELECT created_at FROM students WHERE id = :id"), {"id": student_id})
        existing = check.fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
        
        # تنفيذ التحديث
        conn.execute(
            text("UPDATE students SET name = :name, email = :email, filiere = :filiere WHERE id = :id"),
            {"name": student.name, "email": student.email, "filiere": student.filiere, "id": student_id}
        )
        conn.commit()
        created_at = str(existing[0])
    
    log_to_nosql("UPDATE", "students", student_id, f"Updated student: {student.name}")
    
    return {
        "id": student_id,
        "name": student.name,
        "email": student.email,
        "filiere": student.filiere,
        "created_at": created_at
    }

@app.delete("/sql/students/{student_id}")
def delete_student(student_id: int):
    """حذف طالب من PostgreSQL"""
    with engine.connect() as conn:
        # جلب الاسم للتسجيل
        result = conn.execute(text("SELECT name FROM students WHERE id = :id"), {"id": student_id})
        student = result.fetchone()
        
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
        
        conn.execute(text("DELETE FROM students WHERE id = :id"), {"id": student_id})
        conn.commit()
        student_name = student[0]
    
    log_to_nosql("DELETE", "students", student_id, f"Deleted student: {student_name}")
    
    return {"message": f"Student {student_id} deleted successfully"}

# ==============================================
# 7. API Endpoints للمواد الدراسية (PostgreSQL)
# ==============================================

@app.get("/sql/courses", response_model=List[CourseResponse])
def get_all_courses():
    """جلب جميع المواد من PostgreSQL"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, title, credits, teacher FROM courses ORDER BY id"))
        courses = result.fetchall()
    
    log_to_nosql("READ_ALL", "courses", 0, f"Retrieved {len(courses)} courses")
    
    return [{"id": c[0], "title": c[1], "credits": c[2], "teacher": c[3]} for c in courses]

@app.post("/sql/courses", response_model=CourseResponse)
def create_course(course: Course):
    """إضافة مادة جديدة في PostgreSQL"""
    with engine.connect() as conn:
        result = conn.execute(
            text("INSERT INTO courses (title, credits, teacher) VALUES (:title, :credits, :teacher) RETURNING id"),
            {"title": course.title, "credits": course.credits, "teacher": course.teacher}
        )
        conn.commit()
        course_id = result.fetchone()[0]
    
    log_to_nosql("CREATE", "courses", course_id, f"Created course: {course.title}")
    
    return {
        "id": course_id,
        "title": course.title,
        "credits": course.credits,
        "teacher": course.teacher
    }

@app.post("/sql/inscriptions")
def inscribe_student(inscription: Inscription):
    """تسجيل طالب في مادة (علاقة many-to-many)"""
    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO inscriptions (student_id, course_id) 
                    VALUES (:student_id, :course_id)
                """),
                {"student_id": inscription.student_id, "course_id": inscription.course_id}
            )
            conn.commit()
        
        log_to_nosql(
            "CREATE", "inscriptions", 0, 
            f"Student {inscription.student_id} inscribed in course {inscription.course_id}"
        )
        
        return {"message": "Student inscribed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Inscription already exists or invalid IDs")

@app.get("/sql/students/{student_id}/courses")
def get_student_courses(student_id: int):
    """جلب المواد التي يدرسها طالب معين"""
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT c.id, c.title, c.credits, c.teacher, i.date_inscription
                FROM courses c
                JOIN inscriptions i ON c.id = i.course_id
                WHERE i.student_id = :student_id
            """),
            {"student_id": student_id}
        )
        courses = result.fetchall()
    
    return {
        "student_id": student_id,
        "courses": [
            {
                "id": c[0],
                "title": c[1],
                "credits": c[2],
                "teacher": c[3],
                "inscription_date": str(c[4])
            }
            for c in courses
        ]
    }

# ==============================================
# 8. API Endpoints لـ NoSQL (السجلات والنشاطات)
# ==============================================

@app.get("/nosql/logs")
def get_nosql_logs(limit: int = Query(50, le=100)):
    """جلب آخر السجلات من NoSQL"""
    logs = get_all_logs_from_nosql()
    return {
        "total": len(logs),
        "logs": logs[-limit:] if logs else []
    }

@app.get("/nosql/stats")
def get_nosql_statistics():
    """إحصائيات عن النشاطات من NoSQL"""
    logs = get_all_logs_from_nosql()
    
    stats = {
        "total_actions": len(logs),
        "actions_by_type": {},
        "entities_by_type": {}
    }
    
    for log in logs:
        action = log.get("action", "UNKNOWN")
        entity = log.get("entity", "UNKNOWN")
        
        stats["actions_by_type"][action] = stats["actions_by_type"].get(action, 0) + 1
        stats["entities_by_type"][entity] = stats["entities_by_type"].get(entity, 0) + 1
    
    return stats

@app.post("/nosql/activity")
def add_activity_log(activity: ActivityLog):
    """إضافة سجل نشاط مباشر إلى NoSQL"""
    if activities_collection is not None:
        activities_collection.insert_one(activity.dict())
        return {"message": "Activity logged"}
    else:
        mock_activities.append(activity.dict())
        return {"message": "Activity logged (mock mode)"}

# ==============================================
# 9. API يجمع بين SQL و NoSQL
# ==============================================

@app.get("/combined/dashboard")
def get_combined_dashboard():
    """لوحة تحكم تجمع بيانات PostgreSQL و NoSQL معًا"""
    
    with engine.connect() as conn:
        # عدد الطلاب
        result = conn.execute(text("SELECT COUNT(*) FROM students"))
        total_students = result.fetchone()[0]
        
        # عدد المواد
        result = conn.execute(text("SELECT COUNT(*) FROM courses"))
        total_courses = result.fetchone()[0]
        
        # أعلى 5 طلاب نشاطًا
        result = conn.execute(text("""
            SELECT s.name, COUNT(i.course_id) as courses_count
            FROM students s
            LEFT JOIN inscriptions i ON s.id = i.student_id
            GROUP BY s.id
            ORDER BY courses_count DESC
            LIMIT 5
        """))
        top_students = [{"name": row[0], "courses": row[1]} for row in result.fetchall()]
    
    logs = get_all_logs_from_nosql()
    recent_actions = logs[-10:] if logs else []
    
    action_counts = {}
    for log in logs:
        action = log.get("action", "UNKNOWN")
        action_counts[action] = action_counts.get(action, 0) + 1
    
    return {
        "sql_data": {
            "total_students": total_students,
            "total_courses": total_courses,
            "top_5_active_students": top_students
        },
        "nosql_data": {
            "total_audit_logs": len(logs),
            "recent_actions": recent_actions,
            "action_statistics": action_counts
        },
        "summary": {
            "message": "Data combined from PostgreSQL (students/courses) and MongoDB Atlas (audit logs)",
            "api_version": "2.0.0"
        }
    }

# ==============================================
# 10. Endpoints للاختبار والصحة
# ==============================================

@app.get("/")
def root():
    """الصفحة الرئيسية"""
    return {
        "message": "TP Cloud API - Phase 2",
        "status": "running",
        "databases": {
            "sql": "PostgreSQL on Render",
            "nosql": "MongoDB Atlas" if logs_collection is not None else "MongoDB (mock mode)"
        },
        "endpoints": {
            "sql_students": "/sql/students (GET, POST)",
            "sql_students_id": "/sql/students/{id} (GET, PUT, DELETE)",
            "sql_courses": "/sql/courses (GET, POST)",
            "sql_inscriptions": "/sql/inscriptions (POST)",
            "nosql_logs": "/nosql/logs (GET)",
            "nosql_stats": "/nosql/stats (GET)",
            "combined": "/combined/dashboard (GET)",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """فحص صحة التطبيق وقواعد البيانات"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "postgresql": "checking",
        "mongodb": "connected" if logs_collection is not None else "mock_mode"
    }
    
    # فحص PostgreSQL
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            health_status["postgresql"] = "connected"
    except Exception as e:
        health_status["postgresql"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

@app.get("/seed")
def seed_demo_data():
    """إضافة بيانات تجريبية للاختبار"""
    
    demo_students = [
        ("Ahmed Benali", "ahmed@example.com", "Informatique"),
        ("Sara Kadi", "sara@example.com", "Réseaux"),
        ("Mohamed Lamine", "mohamed@example.com", "Informatique"),
        ("Fatima Zohra", "fatima@example.com", "Mathématiques"),
        ("Yacine Ouali", "yacine@example.com", "Réseaux"),
    ]
    
    demo_courses = [
        ("Cloud Computing", 5, "Dr. Amir"),
        ("Big Data", 4, "Dr. Nadia"),
        ("Machine Learning", 4, "Dr. Karim"),
        ("DevOps", 3, "Mme Leila"),
    ]
    
    with engine.connect() as conn:
        # إضافة الطلاب
        for name, email, filiere in demo_students:
            try:
                conn.execute(
                    text("INSERT INTO students (name, email, filiere) VALUES (:name, :email, :filiere)"),
                    {"name": name, "email": email, "filiere": filiere}
                )
            except Exception:
                pass  # موجود مسبقًا
        
        # إضافة المواد
        for title, credits, teacher in demo_courses:
            try:
                conn.execute(
                    text("INSERT INTO courses (title, credits, teacher) VALUES (:title, :credits, :teacher)"),
                    {"title": title, "credits": credits, "teacher": teacher}
                )
            except Exception:
                pass
        
        conn.commit()
    
    log_to_nosql("SEED", "database", 0, "Added demo data")
    
    return {"message": "Demo data seeded successfully"}

# عند تشغيل الملف مباشرة
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting TP Cloud API - Phase 2...")
    print("🐘 PostgreSQL: on Render")
    print("🍃 MongoDB Atlas: " + ("Connected" if mongo_client else "Mock mode"))
    print("📖 API Docs: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)