import os
import pandas as pd
from uuid import uuid4
from io import BytesIO
from django.apps import apps
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import ImportLog


# ================================================================
# 📥 خطوة 1 — رفع الملف وتخزينه مؤقتًا
# ================================================================
def import_step1_upload(request):
    if request.method == "POST":
        file = request.FILES.get("excel_file")

        if not file:
            messages.error(request, "الرجاء اختيار ملف Excel")
            return redirect("import_app:step1")

        # قراءة أول 5 صفوف فقط لجلب الأعمدة
        try:
            df = pd.read_excel(file, nrows=5)
        except Exception:
            messages.error(request, "صيغة ملف غير صحيحة")
            return redirect("import_app:step1")

        # مسار الملفات المؤقتة
        temp_dir = os.path.join(settings.MEDIA_ROOT, "tmp")
        os.makedirs(temp_dir, exist_ok=True)

        filename = f"{uuid4()}.xlsx"
        filepath = os.path.join(temp_dir, filename)

        # حفظ الملف مؤقتًا
        with open(filepath, "wb") as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        request.session["excel_temp_path"] = filepath
        request.session["excel_columns"] = list(df.columns)

        return redirect("import_app:step2")

    return render(request, "import_app/step1_upload.html")



# ================================================================
# 📦 خطوة 2 — اختيار الجدول
# ================================================================
def import_step2_choose_table(request):
    excel_cols = request.session.get("excel_columns")
    if not excel_cols:
        return redirect("import_app:step1")

    # جلب جميع الجداول المتاحة
    tables = []
    for model in apps.get_models():
        if not model._meta.auto_created:
            tables.append(f"{model._meta.app_label}.{model.__name__}")

    if request.method == "POST":
        table = request.POST.get("table")
        if not table:
            messages.error(request, "الرجاء اختيار جدول")
            return redirect("import_app:step2")

        request.session["selected_table"] = table
        return redirect("import_app:step3")

    return render(
        request,
        "import_app/step2_choose_table.html",
        {"excel_columns": excel_cols, "tables": tables},
    )



# ================================================================
# 🔗 خطوة 3 — مطابقة الأعمدة
# ================================================================
def import_step3_mapping(request):
    excel_cols = request.session.get("excel_columns")
    selected_table = request.session.get("selected_table")

    if not excel_cols or not selected_table:
        return redirect("import_app:step1")

    app_label, model_name = selected_table.split(".")
    model = apps.get_model(app_label, model_name)

    db_fields = [
        f.name for f in model._meta.get_fields()
        if f.concrete and not f.primary_key
    ]

    return render(
        request,
        "import_app/step3_mapping.html",
        {"excel_cols": excel_cols, "db_fields": db_fields},
    )



# ================================================================
# 🚀 خطوة 4 — التنفيذ الفعلي Bulk Create
# ================================================================
def import_step4_apply(request):

    temp_path = request.session.get("excel_temp_path")
    selected_table = request.session.get("selected_table")

    if not temp_path or not selected_table:
        return redirect("import_app:step1")

    # قراءة الملف كاملًا
    df = pd.read_excel(temp_path)

    app_label, model_name = selected_table.split(".")
    model = apps.get_model(app_label, model_name)

    # استخراج المابات من POST
    mappings = {}
    for key, value in request.POST.items():
        if key.startswith("map_") and value != "skip":
            excel_col = key.replace("map_", "")
            mappings[excel_col] = value

    mode = request.POST.get("mode")

    # استبدال البيانات القديمة
    if mode == "replace":
        model.objects.all().delete()

    # تحميل العلاقات Foreign Keys
    relation_cache = {}
    for excel_col, db_field in mappings.items():
        field = model._meta.get_field(db_field)

        if field.is_relation and field.many_to_one:
            rel_model = field.related_model
            relation_cache[db_field] = {
                obj.name.strip(): obj for obj in rel_model.objects.all()
            }

    errors = []
    total = 0
    batch = []
    batch_size = 2000

    for _, row in df.iterrows():
        obj_data = {}

        for excel_col, db_field in mappings.items():
            field = model._meta.get_field(db_field)
            value = row.get(excel_col, None)

            if field.is_relation and field.many_to_one:
                mapping_dict = relation_cache.get(db_field, {})
                instance = mapping_dict.get(str(value).strip())

                if not instance:
                    errors.append(f"{db_field}: القيمة '{value}' غير موجودة")
                    instance = None

                obj_data[db_field] = instance
            else:
                obj_data[db_field] = value

        batch.append(model(**obj_data))

        if len(batch) >= batch_size:
            model.objects.bulk_create(batch, ignore_conflicts=True)
            total += len(batch)
            batch = []

    # آخر دفعة
    if batch:
        model.objects.bulk_create(batch, ignore_conflicts=True)
        total += len(batch)

    # حفظ سجل الاستيراد
    ImportLog.objects.create(
        table_name=selected_table,
        rows_count=total,
        mode=mode,
        status="success" if not errors else "partial",
        message="\n".join(errors)[:1500]
    )

    # حذف TEMP
    if os.path.exists(temp_path):
        os.remove(temp_path)

    messages.success(request, f"✔ تم استيراد {total} سجل (أخطاء: {len(errors)})")
    return redirect("import_app:logs")



# ================================================================
# 📜 عرض السجلات (Logs)
# ================================================================
def import_logs(request):
    logs = ImportLog.objects.order_by("-timestamp")[:100]
    return render(request, "import_app/logs.html", {"logs": logs})
