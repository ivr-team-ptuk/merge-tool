import streamlit as st
import fitz
import io
import zipfile
from streamlit_sortables import sort_items

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="دمج وتقسيم PDF - IVR",
    page_icon="Black_Square-01.svg",
    layout="wide"
)

# =========================
# CONSTANTS
# =========================

LOGO_URL = (
    "https://raw.githubusercontent.com/ivr-team-ptuk/home-page/refs/heads/main/Black_Square-01.svg"
)

# =========================
# CSS
# =========================

with open("styles/style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================
# NAVBAR
# =========================

st.markdown(f"""
<nav class="ivr-navbar">
    <a href="https://ivr-home-page.streamlit.app" class="nav-logo">
        <img src="{LOGO_URL}" class="nav-logo-img" alt="IVR">
    </a>
    <div class="nav-links">
        <a href="https://ivr-watermark-tool.streamlit.app">تعليم الملفات</a>
        <a href="https://ivr-merge-tool.streamlit.app">دمج وتقسيم الملفات</a>
        <a href="https://ivr-imagetopdf-tool.streamlit.app">الصور ↔ PDF</a>
    </div>
</nav>
""", unsafe_allow_html=True)

# =========================
# PAGE HEADER
# =========================

st.markdown(f"""
<div class="page-header">
    <img src="{LOGO_URL}" class="hero-logo" alt="IVR Logo">
    <h1>دمج وتقسيم ملفات PDF</h1>
    <p>ادمج عدة ملفات في واحد أو قسّم ملفاً إلى أجزاء مخصصة</p>
</div>
""", unsafe_allow_html=True)

# =========================
# MODE SELECTOR
# =========================

mode = st.radio(
    "اختر العملية",
    ["🔗  دمج ملفات PDF", "✂️  تقسيم ملف PDF"],
    horizontal=True
)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# LAYOUT
# =========================

controls_col, preview_col = st.columns([1, 1.1])

# =========================================================
# MODE A — MERGE
# =========================================================

if mode.startswith("🔗"):

    # ── Controls ──────────────────────────────────────────
    with controls_col:

        uploaded_pdfs = st.file_uploader(
            "اسحب ملفات PDF هنا أو اضغط للاختيار",
            type=["pdf"],
            accept_multiple_files=True,
            help="يمكنك رفع عدة ملفات دفعة واحدة"
        )

        if uploaded_pdfs:

            st.subheader("ترتيب الملفات")

            sorted_names = sort_items(
                [f.name for f in uploaded_pdfs],
                direction="vertical"
            )

            st.divider()

            add_bookmarks = st.checkbox(
                "إضافة علامات مرجعية",
                value=True
            )

            bookmark_titles = {}

            if add_bookmarks:

                st.subheader("أسماء العلامات المرجعية")

                for name in sorted_names:
                    bookmark_titles[name] = st.text_input(
                        f"علامة: {name}",
                        value=name.removesuffix(".pdf")
                    )

            output_name = st.text_input(
                "اسم الملف النهائي",
                value="merged_file"
            )

            if st.button("دمج وتحميل"):

                file_map    = {f.name: f for f in uploaded_pdfs}
                merged_doc  = fitz.open()
                toc         = []
                current_page = 1
                progress    = st.progress(0)

                for i, name in enumerate(sorted_names):

                    if name not in file_map:
                        continue

                    pdf_doc = fitz.open(
                        stream=file_map[name].getvalue(),
                        filetype="pdf"
                    )
                    merged_doc.insert_pdf(pdf_doc)

                    if add_bookmarks:
                        toc.append([
                            1,
                            bookmark_titles.get(name, name),
                            current_page
                        ])

                    current_page += len(pdf_doc)
                    pdf_doc.close()
                    progress.progress((i + 1) / len(sorted_names))

                if add_bookmarks and toc:
                    merged_doc.set_toc(toc)

                buf = io.BytesIO()
                merged_doc.save(buf)
                merged_doc.close()
                buf.seek(0)

                st.download_button(
                    label="تحميل الملف المدمج",
                    data=buf,
                    file_name=f"{output_name}.pdf",
                    mime="application/pdf"
                )

                st.success("تم الدمج بنجاح 🔥")

        else:
            st.info("قم برفع ملفات PDF أولاً.")

    # ── Preview ───────────────────────────────────────────
    with preview_col:

        st.subheader("المعاينة")

        if uploaded_pdfs:

            try:
                preview_doc = fitz.open(
                    stream=uploaded_pdfs[0].getvalue(),
                    filetype="pdf"
                )
                total_pages = len(preview_doc)

                if total_pages > 1:
                    page_num = st.slider(
                        "الصفحة",
                        min_value=1,
                        max_value=total_pages,
                        value=1
                    )
                else:
                    page_num = 1
                    st.caption("الملف يحتوي على صفحة واحدة فقط")

                page = preview_doc[page_num - 1]
                pix  = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                st.image(pix.tobytes("png"), use_container_width=True)
                preview_doc.close()

            except Exception as e:
                st.error(f"خطأ في المعاينة: {e}")

        else:
            st.info("قم برفع ملف لرؤية المعاينة.")

# =========================================================
# MODE B — SPLIT
# =========================================================

else:

    # ── Controls ──────────────────────────────────────────
    with controls_col:

        uploaded_pdf = st.file_uploader(
            "اسحب ملف PDF هنا أو اضغط للاختيار",
            type=["pdf"],
            accept_multiple_files=False,
            help="ملف PDF واحد فقط"
        )

        if uploaded_pdf:

            _doc = fitz.open(stream=uploaded_pdf.getvalue(), filetype="pdf")
            total_pages = len(_doc)
            _doc.close()

            st.caption(f"إجمالي الصفحات: **{total_pages}**")
            st.divider()

            num_files = st.number_input(
                "عدد الملفات الناتجة",
                min_value=2,
                max_value=total_pages,
                value=2,
                step=1
            )
            num_files = int(num_files)

            st.subheader("تحديد نطاق كل ملف")

            splits = []

            for i in range(num_files):

                st.markdown(f"**── الملف {i + 1}**")
                c1, c2 = st.columns(2)

                with c1:
                    start = st.number_input(
                        "من صفحة",
                        min_value=1,
                        max_value=total_pages,
                        value=1,
                        key=f"start_{i}"
                    )

                with c2:
                    end = st.number_input(
                        "إلى صفحة",
                        min_value=1,
                        max_value=total_pages,
                        value=total_pages,
                        key=f"end_{i}"
                    )

                fname = st.text_input(
                    "اسم الملف الناتج",
                    value=f"part_{i + 1}",
                    key=f"name_{i}"
                )

                splits.append((int(start), int(end), fname))

            st.divider()

            if st.button("تقسيم وتحميل"):

                errors = [i + 1 for i, (s, e, _) in enumerate(splits) if s > e]

                if errors:
                    st.error(
                        f"خطأ في الملفات: {errors} — صفحة البداية يجب أن تكون ≤ صفحة النهاية."
                    )

                else:
                    zip_buf  = io.BytesIO()
                    progress = st.progress(0)

                    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:

                        for i, (start, end, fname) in enumerate(splits):

                            src = fitz.open(
                                stream=uploaded_pdf.getvalue(),
                                filetype="pdf"
                            )
                            new_doc = fitz.open()
                            new_doc.insert_pdf(
                                src,
                                from_page=start - 1,
                                to_page=end - 1
                            )
                            buf = io.BytesIO()
                            new_doc.save(buf)
                            new_doc.close()
                            src.close()
                            buf.seek(0)
                            zf.writestr(f"{fname}.pdf", buf.read())
                            progress.progress((i + 1) / len(splits))

                    zip_buf.seek(0)

                    st.download_button(
                        label="تحميل الملفات (ZIP)",
                        data=zip_buf,
                        file_name="split_files.zip",
                        mime="application/zip"
                    )

                    st.success("تم التقسيم بنجاح 🔥")

        else:
            st.info("قم برفع ملف PDF أولاً.")

    # ── Preview ───────────────────────────────────────────
    with preview_col:

        st.subheader("المعاينة")

        if uploaded_pdf:

            try:
                preview_doc = fitz.open(
                    stream=uploaded_pdf.getvalue(),
                    filetype="pdf"
                )
                total_pages = len(preview_doc)

                if total_pages > 1:
                    page_num = st.slider(
                        "الصفحة",
                        min_value=1,
                        max_value=total_pages,
                        value=1
                    )
                else:
                    page_num = 1
                    st.caption("الملف يحتوي على صفحة واحدة فقط")

                page = preview_doc[page_num - 1]
                pix  = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                st.image(pix.tobytes("png"), use_container_width=True)
                preview_doc.close()

            except Exception as e:
                st.error(f"خطأ في المعاينة: {e}")

        else:
            st.info("قم برفع ملف لرؤية المعاينة.")

# =========================
# FOOTER
# =========================

st.markdown(
    '<div class="footer">IVR Engineering Society © 2026</div>',
    unsafe_allow_html=True
)